require(pscl)
require(MASS)

args = commandArgs(trailingOnly=TRUE)
print(length(args))
print(args[1])
print(args[2])
print(args[3])

fn <- args[1]
file_dir <- args[2]
model <- args[3]

data <- read.csv(file=file.path(file_dir, fn), header=TRUE, sep=",")

if (model == "poisson") {
  results <- glm(y ~ . - 1, data = data, family=poisson())
} else if (model == "gaussian") {
  results <- glm(y ~ . - 1, data = data, family=gaussian())
} else if (model == "quasipoisson") {
  results <- glm(y ~ . - 1, data = data, family=quasipoisson())
} else if (model == "nb") {
  results <- glm.nb(y ~ . - 1, data=data)
} else if (model == "hurdlepoisson") {
  results <- hurdle(y ~ . - 1, data=data, dist="poisson")
} else if (model == "hurdlegeometric") {
  results <- hurdle(y ~ . - 1, data=data, dist="geometric")
} else if (model == "hurdlenegbin"){
  results <- hurdle(y ~ . - 1, data=data, dist="negbin")
}
  
#summary(results)

results_df <- summary(results)$coefficients
data$fit <- fitted(results)

write.csv(results_df, file.path(file_dir, 'r_summary.csv'))
write.csv(data, file.path(file_dir, 'fit.csv'))