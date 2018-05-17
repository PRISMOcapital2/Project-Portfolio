### Mean Reverting Trade Strategy

## 17/05/2018
The aim is to build a live platform that trades off a mean reverting strategy. To implement such a strategy, we need a stationary time series. All the time series that we deal with will not be stationary in their given form, so we must transform them. As is my other projects, I will be testing on bitcoin as its the omst readily available currencey that I have access to the data of. 

Once the data has been pulled and arrayed, we want to see what its like in its raw form so we inspect the autocorrelations of the data. (Recall that a stationary time series has no autocorrelations in residuals). Log returns are usually stationary about a mean zero, so that it the first transformation we need to make. 

Next is the testing of stationarity. " If the hypothesis λ = 0 can be rejected, that means the next move Δy(t) depends on the current level y(t − 1)" - Ernie Chan. The test statistic for this is  λ/SE(λ), and is regressed on Δy(t) = λy(t − 1) + μ + βt + α1Δy(t − 1) + … + αkΔy(t − k) + ∋(t). When we run such a test on white noise, or on a sin plot for a set period, we know these periods are mean reverting and that λ!=0, so they are good test cases as proofs of concept.

<p align="center">
  <img src="whitenoiseADF.png" width="350"/>
  <img src="sinADF.png" width="350"/>
</p>
