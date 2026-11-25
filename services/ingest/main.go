// ingest: a tiny HTTP collector. Your agent POSTs each trace here; we append
// it to a JSONL file that tracetune (Python) can read later.
// Why Go: cheap concurrency, one static binary, ideal for network services.
package main

import (
	"encoding/json"
	"io"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"sync"
)

var mu sync.Mutex

func env(k, def string) string {
	if v := os.Getenv(k); v != "" {
		return v
	}
	return def
}

func main() {
	path := env("TRACES_FILE", "data/traces.jsonl")
	addr := env("ADDR", ":8080")
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		log.Fatal(err)
	}

	http.HandleFunc("/healthz", func(w http.ResponseWriter, _ *http.Request) {
		_, _ = w.Write([]byte("ok"))
	})

	http.HandleFunc("/v1/traces", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "POST only", http.StatusMethodNotAllowed)
			return
		}
		body, err := io.ReadAll(http.MaxBytesReader(w, r.Body, 1<<20))
		if err != nil {
			http.Error(w, "body too large", http.StatusRequestEntityTooLarge)
			return
		}
		var t map[string]any
		if json.Unmarshal(body, &t) != nil {
			http.Error(w, "invalid JSON", http.StatusBadRequest)
			return
		}
		for _, k := range []string{"trace_id", "input", "output"} {
			if _, ok := t[k]; !ok {
				http.Error(w, "missing field: "+k, http.StatusBadRequest)
				return
			}
		}
		line, _ := json.Marshal(t)

		mu.Lock()
		defer mu.Unlock()
		f, err := os.OpenFile(path, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0o644)
		if err != nil {
			http.Error(w, "storage error", http.StatusInternalServerError)
			return
		}
		defer f.Close()
		_, _ = f.Write(append(line, '\n'))
		w.WriteHeader(http.StatusAccepted)
	})

	log.Printf("ingest listening on %s, writing to %s", addr, path)
	log.Fatal(http.ListenAndServe(addr, nil))
}
