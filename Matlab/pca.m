function [signals,PC,V] = pca(data)
% PCA2: Perform PCA using SVD.
% data-MxNmatrixofinputdata
% (M dimensions, N trials)
% signals - MxN matrix of projected data
% PC - each column is a PC
% V- Mx1 matrix of variances
[~,N] = size(data);
% subtract off the mean for each dimension
mn = mean(data,2);
data = data - repmat(mn,1,N);
% construct the matrix Y
Y = data'/ sqrt(N-1);
% SVD does it all
[~,S,PC] = svd(Y);
% calculate the variances
S = diag(S);
V = S .* S;
% project the original data
signals = PC' * data;