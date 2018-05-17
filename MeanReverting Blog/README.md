### Mean Reverting Trade Strategy

## 17/05/2018
The aim is to build a live platform that trades off a mean reverting strategy. To implement such a strategy, we need a stationary time series. All the time series that we deal with will not be stationary in their given form, so we must transform them. As is my other projects, I will be testing on bitcoin as its the omst readily available currencey that I have access to the data of. 

Once the data has been pulled and arrayed, we want to see what its like in its raw form so we inspect the autocorrelations of the data. (Recall that a stationary time series has no autocorrelations in residuals). Log returns are usually stationary about a mean zero, so that it the first transformation we need to make. 
