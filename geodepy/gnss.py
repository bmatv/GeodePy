#!/usr/bin/env python3

"""
Geoscience Australia - Python Geodesy Package
GNSS Module

In Development
"""
from numpy import zeros


def read_sinex_estimate(file):
    """This function reads in the SOLUTION/ESTIMATE block of a SINEX file. It
    returns estimate, a list of tuples:

    estimate = [(code, soln, refEpoch, staX, staY, staZ, staX_sd, staY_sd,
                 staZ_sd[, velX, velY, velZ, velX_sd, velY_sd, velZ_sd])...]

    where:
        * code is the stations's 4-character ID
        * soln is the segment of the stations's time series
        * refEpoch is the epoch of the solution in the form YY:DOY:SSSSS (YY
            is the two digit year, DOY is day of year, and SSSSS is the time of
            day in seconds
        * sta[XYZ] is the station coordinates in the Cartesian reference frame
        * sta[XYZ]_sd is the standard deviation of the station coordinates in
            the Cartesian reference frame
        * vel[XYZ] is the station velocity in the Cartesian reference frame
        * vel[XYZ]_sd is the standard deviation of the station velocity in the
            Cartesian reference frame

    Velocities are not included in all SINEX files and so are only returned if
    present.

    :param file: the input SINEX file
    :return: estimate
    """

    # Create data structures and set variables
    lines = []
    estimate = []
    velocities = False
    go = False
    code = ''
    soln = ''
    epoch = ''
    stax = ''
    stay = ''
    staz = ''
    stax_sd = ''
    stay_sd = ''
    staz_sd = ''
    velx = ''
    vely = ''
    velz = ''
    velx_sd = ''
    vely_sd = ''
    velz_sd = ''

    # Read the SOLUTION/ESTIMATE block into a list and determine if there is
    # any velocity information
    with open(file) as f:
        for line in f:
            if line[:18] == '-SOLUTION/ESTIMATE':
                break
            if go and line[:11] == '*INDEX TYPE':
                pass
            elif go:
                if line[7:10] == 'VEL':
                    velocities = True
                lines.append(line)
            if line[:18] == '+SOLUTION/ESTIMATE':
                go = True

    for line in lines:
        typ = line[7:11]
        if typ == 'STAX':
            code = line[14:18]
            soln = line[23:26].lstrip()
            epoch = line[27:39]
            stax = float(line[47:68])
            stax_sd = float(line[69:80])
        elif typ == 'STAY':
            stay = float(line[47:68])
            stay_sd = float(line[69:80])
        elif typ == 'STAZ':
            staz = float(line[47:68])
            staz_sd = float(line[69:80])
            if not velocities:
                info = (code, soln, epoch, stax, stay, staz, stax_sd, stay_sd,
                        staz_sd)
                estimate.append(info)
        elif typ == 'VELX':
            velx = float(line[47:68])
            velx_sd = float(line[69:80])
        elif typ == 'VELY':
            vely = float(line[47:68])
            vely_sd = float(line[69:80])
        elif typ == 'VELZ':
            velz = float(line[47:68])
            velz_sd = float(line[69:80])
            info = (code, soln, epoch, stax, stay, staz, stax_sd, stay_sd,
                    staz_sd, velx, vely, velz, velx_sd, vely_sd, velz_sd)
            estimate.append(info)

    return estimate


def read_sinex_matrix(file):

    """This function reads in the SOLUTION/MATRIX_ESTIMATE block of a SINEX
    file. It returns matrix, a list of tuples:

    matrix = [(code, soln, var_x, covar_xy, covar_xz, var_y, covar_yz,
            var_z[, var_v_x, covar_v_xy, covar_v_xz, var_v_y, covar_v_yz,
            var_v_z])...]

    where:
        * code is the stations's 4-character ID
        * soln is the segment of the stations's time series
        * var_x is the variance in the X coordinate
        * covar_xy is the covariance between the X and the Y coordinates
        * covar_xz is the covariance between the X and the Z coordinates
        * var_y is the variance in the Y coordinate
        * covar_yz is the covariance between the Y and the Z coordinates
        * var_z is the variance in the Z coordinate
        * var_v_x is the variance in the X velocity
        * covar_v_xy is the covariance between the X and the Y velocities
        * covar_v_xz is the covariance between the X and the Z velocities
        * var_v_y is the variance in the Y velocity
        * covar_v_yz is the covariance between the Y and the Z velocities
        * var_v_z is the variance in the Z velocity

    Velocities are not included in all SINEX files and so their VCV information
    is only returned if they are present.

    :param file: the input SINEX file
    :return: matrix
    """

    # Read in the codes (station names) and solutions, and check for velocities
    data = read_sinex_estimate(file)
    code = []
    soln = []
    velocities = False
    for station in data:
        code.append(station[0])
        soln.append(station[1])
    if len(data[0]) == 15:
        velocities = True

    # Read the SOLUTION/MATRIX_ESTIMATE block into a list and determine if the
    # matrix is upper or lower triangular
    lines = []
    lower_triangular = False
    go = False
    with open(file) as f:
        for line in f:
            if line[:25] == '-SOLUTION/MATRIX_ESTIMATE':
                break
            if go and line[:12] == '*PARA1 PARA2':
                pass
            elif go:
                lines.append(line)
            if line[:25] == '+SOLUTION/MATRIX_ESTIMATE':
                if line[26] == 'L':
                    lower_triangular = True
                go = True

    # Create an array containing the matrix elements
    if velocities:
        n = 6 * int(len(code))
    else:
        n = 3 * int(len(code))
    element = zeros((n, n))
    matrix = []
    for line in lines:
        col = line.rstrip().split()
        for i in range(2, len(col)):
            element[int(col[0]) - 1][int(col[1]) + i - 3] = float(col[i])
    if velocities:
        if lower_triangular:
            for i in range(len(code)):
                info = (code[i], soln[i], element[6 * i][6 * i],
                        element[6 * i + 1][6 * i],
                        element[6 * i + 1][6 * i + 1],
                        element[6 * i + 2][6 * i],
                        element[6 * i + 2][6 * i + 1],
                        element[6 * i + 2][6 * i + 2],
                        element[6 * i + 3][6 * i + 3],
                        element[6 * i + 4][6 * i + 3],
                        element[6 * i + 4][6 * i + 4],
                        element[6 * i + 5][6 * i + 3],
                        element[6 * i + 5][6 * i + 4],
                        element[6 * i + 5][6 * i + 5])
                matrix.append(info)
        else:
            for i in range(len(code)):
                info = (code[i], soln[i], element[6 * i][6 * i],
                        element[6 * i][6 * i + 1], element[6 * i][6 * i + 2],
                        element[6 * i + 1][6 * i + 1],
                        element[6 * i + 1][6 * i + 2],
                        element[6 * i + 2][6 * i + 2],
                        element[6 * i + 3][6 * i + 3],
                        element[6 * i + 3][6 * i + 4],
                        element[6 * i + 3][6 * i + 5],
                        element[6 * i + 4][6 * i + 4],
                        element[6 * i + 4][6 * i + 5],
                        element[6 * i + 5][6 * i + 5])
                matrix.append(info)
    else:
        if lower_triangular:
            for i in range(len(code)):
                info = (code[i], soln[i], element[3 * i][3 * i],
                        element[3 * i + 1][3 * i],
                        element[3 * i + 1][3 * i + 1],
                        element[3 * i + 2][3 * i],
                        element[3 * i + 2][3 * i + 1],
                        element[3 * i + 2][3 * i + 2])
                matrix.append(info)
        else:
            for i in range(len(code)):
                info = (code[i], soln[i], element[3 * i][3 * i],
                        element[3 * i][3 * i + 1], element[3 * i][3 * i + 2],
                        element[3 * i + 1][3 * i + 1],
                        element[3 * i + 1][3 * i + 2],
                        element[3 * i + 2][3 * i + 2])
                matrix.append(info)

    return matrix
