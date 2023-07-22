"""Matrix utility functions"""

import numpy as np

def reduced_row_echelon_form(mat):
    """Compute the reduced row echelon form of a matrix"""
    height, width = mat.shape

    res = np.identity(height, np.uint8)
    pivot = 0
    for i in range(width):
        isfound = False
        for j in range(i, height):
            if mat[j, i]:
                if isfound:
                    mat[j] ^= mat[pivot]
                    res[j] ^= res[pivot]
                else:
                    isfound = True
                    mat[[j, pivot]] = mat[[pivot, j]]
                    res[[j, pivot]] = res[[pivot, j]]
        if isfound:
            pivot += 1
    return mat, res

def mat_inverse(mat, verify_invertible: bool = True):
    """Compute the inverse of a GF(2) matrix via gauss jordan elimination"""
    _, width = mat.shape
    mat, res = reduced_row_echelon_form(mat)

    if verify_invertible:
        for i in range(width):
            assert mat[i, i], "Matrix is not invertible"

    for i in range(1, width)[::-1]:
        for j in range(i)[::-1]:
            if mat[j, i]:
                mat[j] ^= mat[i]
                res[j] ^= res[i]
    return res[:width]

def inverse_proress(mat):
    """Compute an estimation of the invertibility of the matrix"""
    height, width = mat.shape
    mat, _ = reduced_row_echelon_form(mat)

    progress = 0

    for i in range(min(width, height)):
        progress += mat[i, i]

    return (progress, width)
