# Build the CCME guarantees report.
#
# Tectonic is used rather than a full TeX installation: it needs no local
# package tree, fetches what the document asks for on first run, and caches it.
#
#   brew install tectonic          # macOS
#   cargo install tectonic         # anywhere with Rust

TECTONIC ?= tectonic
OUT      := build
MAIN     := main.tex
SRC      := $(MAIN) preamble.tex macros.tex $(wildcard sections/*.tex) $(wildcard appendix/*.tex)

.PHONY: pdf watch clean check

pdf: $(OUT)/main.pdf

$(OUT)/main.pdf: $(SRC)
	@mkdir -p $(OUT)
	$(TECTONIC) --outdir $(OUT) --keep-logs --print $(MAIN)

# Rebuild on every save. Tectonic's own watcher needs `tectonic -X`; this works
# with the plain driver too.
watch:
	@while true; do $(MAKE) --no-print-directory pdf; \
	  fswatch -1 $(SRC) >/dev/null 2>&1 || sleep 2; done

# The build is only clean if the log is clean: an undefined reference is a
# broken cross-reference in the finished PDF, not a warning to live with.
check: pdf
	@if grep -qE 'Reference .* undefined|multiply.defined|There were undefined' $(OUT)/main.log; then \
	  echo "FAIL: unresolved references"; \
	  grep -nE 'Reference .* undefined|multiply.defined' $(OUT)/main.log; exit 1; \
	fi
	@echo "OK: no undefined or duplicate references"
	@n=$$(grep -c 'Overfull' $(OUT)/main.log || true); echo "overfull boxes: $$n"

clean:
	rm -rf $(OUT)
