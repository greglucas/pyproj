import numpy
import pytest
from numpy.testing import assert_allclose, assert_almost_equal

from pyproj import Proj, __proj_version__, transform
from test.conftest import PROJ_911, PROJ_GTE_92, PROJ_GTE_911, grids_available


def test_transform():
    # convert awips221 grid to awips218 coordinate system
    # (grids defined at http://www.nco.ncep.noaa.gov/pmb/docs/on388/tableb.html)
    nx = 614
    ny = 428
    dx = 12190.58
    dy = dx
    awips221 = Proj(proj="lcc", R=6371200, lat_1=50, lat_2=50, lon_0=-107)
    print("proj4 library version = ", __proj_version__)
    llcrnrx, llcrnry = awips221(-145.5, 1)
    awips221 = Proj(
        proj="lcc",
        R=6371200,
        lat_1=50,
        lat_2=50,
        lon_0=-107,
        x_0=-llcrnrx,
        y_0=-llcrnry,
    )
    assert_allclose(awips221(-145.5, 1), (0, 0), atol=1e-4)
    awips218 = Proj(proj="lcc", R=6371200, lat_1=25, lat_2=25, lon_0=-95)
    llcrnrx, llcrnry = awips218(-133.459, 12.19)
    awips218 = Proj(
        proj="lcc", R=6371200, lat_1=25, lat_2=25, lon_0=-95, x_0=-llcrnrx, y_0=-llcrnry
    )
    assert_allclose(awips218(-133.459, 12.19), (0, 0), atol=1e-4)
    x1 = dx * numpy.indices((ny, nx), "f")[1, :, :]
    y1 = dy * numpy.indices((ny, nx), "f")[0, :, :]
    print("max/min x and y for awips218 grid")
    print(numpy.minimum.reduce(numpy.ravel(x1)), numpy.maximum.reduce(numpy.ravel(x1)))
    print(numpy.minimum.reduce(numpy.ravel(y1)), numpy.maximum.reduce(numpy.ravel(y1)))
    with pytest.warns(FutureWarning):
        x2, y2 = transform(awips218, awips221, x1, y1)
    print("max/min x and y for awips218 grid in awips221 coordinates")
    print(numpy.minimum.reduce(numpy.ravel(x2)), numpy.maximum.reduce(numpy.ravel(x2)))
    print(numpy.minimum.reduce(numpy.ravel(y2)), numpy.maximum.reduce(numpy.ravel(y2)))
    with pytest.warns(FutureWarning):
        x3, y3 = transform(awips221, awips218, x2, y2)
    print("error for reverse transformation back to awips218 coords")
    print("(should be close to zero)")
    assert_allclose(numpy.minimum.reduce(numpy.ravel(x3 - x1)), 0, atol=1e-4)
    assert_allclose(numpy.maximum.reduce(numpy.ravel(x3 - x1)), 0, atol=1e-4)
    assert_allclose(numpy.minimum.reduce(numpy.ravel(y3 - y1)), 0, atol=1e-4)
    assert_allclose(numpy.maximum.reduce(numpy.ravel(y3 - y1)), 0, atol=1e-4)


@pytest.mark.xfail(PROJ_911, reason="Patch applied in conda-forge changes behavior")
def test_transform_single_point_nad83_to_nad27():
    # projection 1: UTM zone 15, grs80 ellipse, NAD83 datum
    # (defined by epsg code 26915)
    p1 = Proj("epsg:26915", preserve_units=False)
    # projection 2: UTM zone 15, clrk66 ellipse, NAD27 datum
    p2 = Proj("epsg:26715", preserve_units=False)
    # find x,y of Jefferson City, MO.
    x1, y1 = p1(-92.199881, 38.56694)
    # transform this point to projection 2 coordinates.
    x2, y2 = transform(p1, p2, x1, y1)
    assert_almost_equal(
        (x1, y1),
        (569704.566, 4269024.671),
        decimal=3,
    )
    expected_xy2 = (569722, 4268814)
    if PROJ_GTE_911:
        expected_xy2 = (569720, 4268813)
        if (
            PROJ_GTE_92
            and grids_available(
                "us_noaa_nadcon5_nad27_nad83_1986_conus.tif", check_network=False
            )
        ) or grids_available():
            expected_xy2 = (569722, 4268814)
        elif grids_available(
            "ca_nrc_ntv2_0.tif", "ca_nrc_ntv1_can.tif", check_network=False
        ):
            expected_xy2 = (569706, 4268817)
        elif grids_available("us_noaa_conus.tif", check_network=False):
            expected_xy2 = (569722, 4268814)

    assert_almost_equal(
        (x2, y2),
        expected_xy2,
        decimal=0,
    )
    assert_almost_equal(
        p2(x2, y2, inverse=True, errcheck=True),
        (-92.200, 38.567),
        decimal=3,
    )


@pytest.mark.xfail(PROJ_911, reason="Patch applied in conda-forge changes behavior")
def test_transform_tuple_nad83_to_nad27():
    # projection 1: UTM zone 15, grs80 ellipse, NAD83 datum
    # (defined by epsg code 26915)
    p1 = Proj("epsg:26915", preserve_units=False)
    # projection 2: UTM zone 15, clrk66 ellipse, NAD27 datum
    p2 = Proj("epsg:26715", preserve_units=False)
    # process 3 points at a time in a tuple
    lats = (38.83, 39.32, 38.75)  # Columbia, KC and StL Missouri
    lons = (-92.22, -94.72, -90.37)
    x1, y1 = p1(lons, lats)
    x2, y2 = transform(p1, p2, x1, y1)
    assert_almost_equal(
        x1,
        (567703.344, 351730.944, 728553.093),
        decimal=3,
    )
    assert_almost_equal(
        y1,
        (4298200.739, 4353698.725, 4292319.005),
        decimal=3,
    )
    expected_x2 = (567721, 351747, 728569)
    expected_y2 = (4297989, 4353489, 4292106)
    if PROJ_GTE_911:
        expected_x2 = (567719, 351748, 728568)
        expected_y2 = (4297989, 4353487, 4292108)
        if (
            PROJ_GTE_92
            and grids_available(
                "us_noaa_nadcon5_nad27_nad83_1986_conus.tif", check_network=False
            )
        ) or grids_available():
            expected_x2 = (567721, 351747, 728569)
            expected_y2 = (4297989, 4353489, 4292106)
        elif grids_available(
            "ca_nrc_ntv2_0.tif", "ca_nrc_ntv1_can.tif", check_network=False
        ):
            expected_x2 = (567705, 351727, 728558)
            expected_y2 = (4297993, 4353490, 4292111)
        elif grids_available("us_noaa_conus.tif", check_network=False):
            expected_x2 = (567721, 351747, 728569.133)
            expected_y2 = (4297989, 4353489, 4292106)

    assert_almost_equal(
        x2,
        expected_x2,
        decimal=0,
    )
    assert_almost_equal(
        y2,
        expected_y2,
        decimal=0,
    )
    lons2, lats2 = p2(x2, y2, inverse=True, errcheck=True)
    assert_almost_equal(
        lons2,
        (-92.220, -94.720, -90.370),
        decimal=3,
    )
    assert_almost_equal(
        lats2,
        (38.830, 39.320, 38.750),
        decimal=3,
    )
