require(pscl)
require(MASS)

fn = "data.csv"
file_dir = "."

data <- read.csv(file=file.path(file_dir, fn), header=TRUE, sep=",")
results <- hurdle(y ~ . - 1, data=data, dist="poisson")
results <- glm(y ~ . - 1, data=data, family=poisson())
results <- glm.nb(y ~ . - 1, data=data)

summary(results)
results$residuals

results_df <- summary.glm(results)$coefficients
data$fit <- fitted(results)

write.csv(results_df, file.path(file_dir, 'r_summary.csv'))
write.csv(data, file.path(file_dir, fn))