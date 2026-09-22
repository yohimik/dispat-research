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

# ---- condensed edition ------------------------------------------------------
# report.tex shares the section files with main.tex and references results
# that only the extended edition holds through a generated label shim.
REPORT_SRC := report.tex preamble.tex macros.tex \
  sections/01-findings.tex sections/02-model.tex sections/03-propagation.tex \
  sections/04-protocol.tex sections/04a-durations.tex sections/05-guarantees.tex \
  sections/06-determinism.tex sections/07-duality.tex sections/09-departures.tex \
  sections/11-results.tex appendix/a-notation.tex appendix/b-abstract.tex \
  sections/99-references.tex

.PHONY: report check-report shim

# The extended edition must be built with its .aux kept before the shim exists.
$(OUT)/main.aux: $(SRC)
	@mkdir -p $(OUT)
	$(TECTONIC) --outdir $(OUT) --keep-logs --keep-intermediates $(MAIN)

shim: $(OUT)/labels-from-full.tex
$(OUT)/labels-from-full.tex: $(OUT)/main.aux tools/make-label-shim.py $(REPORT_SRC)
	python3 tools/make-label-shim.py $(OUT)/main.aux $@ $(REPORT_SRC)

report: $(OUT)/report.pdf
$(OUT)/report.pdf: $(REPORT_SRC) $(OUT)/labels-from-full.tex
	$(TECTONIC) --outdir $(OUT) --keep-logs --print report.tex

check-report: report
	@if grep -qE 'Reference .* undefined|multiply.defined|There were undefined' $(OUT)/report.log; then \
	  echo "FAIL: unresolved references in the condensed edition"; \
	  grep -nE 'Reference .* undefined|multiply.defined' $(OUT)/report.log; exit 1; \
	fi
	@echo "OK: condensed edition has no undefined or duplicate references"
	@n=$$(grep -c 'Overfull' $(OUT)/report.log || true); echo "overfull boxes: $$n"
