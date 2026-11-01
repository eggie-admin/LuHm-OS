#!/usr/bin/env Rscript
# LuHm-OS base R only. Bounded, deterministic SYNTHETIC parameter grid.
# No package installs, shell, exec, real kernel writes, passwords or network.
args <- commandArgs(trailingOnly = TRUE)

parse_bound <- function(raw, min_value, max_value) {
  if (!is.character(raw) || length(raw) != 1 ||
      !grepl("^(0|[1-9][0-9]{0,1})$", raw)) stop("RED_R_BOUND")
  n <- as.integer(raw)
  if (is.na(n) || n < min_value || n > max_value) stop("RED_R_BOUND")
  n
}

if (identical(args, "--self-test")) {
  target <- 2L
  candidates <- 0:4
} else {
  if (length(args) != 2 ||
      !grepl("^--target=", args[1]) ||
      !grepl("^--candidates=", args[2])) stop("RED_R_ARGS")
  target <- parse_bound(sub("^--target=", "", args[1]), 0L, 10L)
  raw <- sub("^--candidates=", "", args[2])
  if (nchar(raw) > 47 || !grepl("^[0-9]+(,[0-9]+){0,15}$", raw)) {
    stop("RED_R_GRID")
  }
  pieces <- strsplit(raw, ",", fixed = TRUE)[[1]]
  if (length(pieces) > 16) stop("RED_R_TRIAL_LIMIT")
  candidates <- vapply(pieces, parse_bound, integer(1), min_value=0L, max_value=15L)
  if (anyDuplicated(candidates)) stop("RED_R_DUPLICATE")
}
if (length(candidates) < 1 || length(candidates) > 16) stop("RED_R_TRIAL_LIMIT")
# Source-only synthetic score. The regularization discourages excess size.
score <- (as.numeric(candidates) - as.numeric(target))^2 +
         0.1 * as.numeric(candidates)^2
sorted <- order(score, candidates, method = "radix")
best <- candidates[sorted[1]]
cat("schema=luhmOs.syntheticRTune.v1\n")
cat(paste0("best=", best, "\n"))
cat(paste0("trials=", length(candidates), "\n"))
cat("state=SYNTHETIC_ONLY_NOT_REAL_KERNEL_OR_AGENT_TUNING\n")
cat("runtimeRights=HOLD\n")
