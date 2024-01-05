.SECONDEXPANSION:
.PHONY: latex
latex:
	$(MAKE) -C latex

# directories that contain .txt files of measurement logs
L4_DATA_DIRS := l4-cpp l4-cpp-diff l4-py
OW_DATA_DIRS := ow-data ow-keepwarm

DATA_DIRS := $(L4_DATA_DIRS) $(OW_DATA_DIRS)

L4_PREPROCESS_RULES := $(addprefix preprocess-,$(L4_DATA_DIRS))
OW_PREPROCESS_RULES := $(addprefix preprocess-,$(OW_DATA_DIRS))
# l4 and ow need different preprocessing since they have
# different commandline output
.PHONY: preprocess-all
preprocess-all: $(L4_PREPROCESS_RULES) $(OW_PREPROCESS_RULES)

# preprocess single l4 measurement directory
.PHONY: $(L4_PREPROCESS_RULES)
$(L4_PREPROCESS_RULES): preprocess-%: $$(wildcard %/*.txt)
	./preprocess_l4.py $^

# preprocess single ow measurement directory
.PHONY: $(OW_PREPROCESS_RULES)
$(OW_PREPROCESS_RULES): preprocess-%: $$(wildcard %/*.txt)
	./preprocess_ow.py $^

BENCHMARK_RULES := $(addprefix benchmark-,$(DATA_DIRS))
# the benchmark processing step extracts multi metrics out
# of the raw measurement time stamps
benchmark-all: $(BENCHMARK_RULES)

.PHONY: $(BENCHMARK_RULES)
$(BENCHMARK_RULES): benchmark-%: %/
	./benchmark.py $* $(addsuffix .csv,$*)


.PHONY: clean
clean:
	rm -f $(addsuffix .csv, $(DATA_DIRS))
	rm -f $(foreach dir,$(DATA_DIRS),$(wildcard $(dir)/*.json))
	$(MAKE) -C latex clean

