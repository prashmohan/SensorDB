function [EOFs,PCs,Var,Xrecon] = principal_component_analysis(X,neof)
% function [EOFs,PCs,Var]=principal_component_analysis(X,neof)
% Function to do a principal component analysis of 
% data matrix X. 
% Input:
%   X: (t,x) each row corrsponds to a sample, each column 
%      is a variable. (Each column is a time series of a 
%      variable.)
%   neof: number of EOF/PC to return
% Output:
%   EOFs: (x,e) matrix with EOFs (loadings) in the columns
%   PCs:  (t,e) matrix with principal components (scores) in the columns
%   Var:  variance of each principal component
%   Xrecon: (t,x) reconstructed X (WITHOUT adding back the mean)
% To reconstruct: Xrecon = PCs*EOFs'
% Notes: (1) This routine will subtract off the mean of each 
%            variable (column) before performing PCA.
%        (2) sum(var(X)) = sum(Var) = sum(diag(S)^2/(m-1))

if strcmp(class(X),'single')
  disp('WARNING: Converting input matrix X to class DOUBLE')
end  

% Center X by subtracting off column means
[m,n] = size(X);
X = X - repmat(mean(X,1),m,1);
r = min(m-1,n); % max possible rank of X

% SVD
if nargin < 2
   [U,S,EOFs]=svds(X,r);
else
   [U,S,EOFs]=svds(X,min(r,neof));
end

% EOFs: (x,e)
% U: (t,e)

% Determine the EOF coefficients
PCs=U*S; % PCs=X*EOFs (t,e)

% compute variance of each PC
Var=diag(S).^2/(m-1);

% Note: X = U*S*EOFs'
%       EOFs are eigenvectors of X'*X = (m-1)*cov(X)
%       sig^2 (=diag(S)^2) are eigenvalues of X'*X
%       So tr(X'*X) = sum(sig_i^2) = (m-1)*(total variance of X)

if nargout>3
  Xrecon = PCs*EOFs'; % (t,x)
end