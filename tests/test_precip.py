from xclim import precip
import xarray as xr
import numpy as np
import os
import pandas as pd

TESTS_HOME = os.path.abspath(os.path.dirname(__file__))
TESTS_DATA = os.path.join(TESTS_HOME, 'testdata')
K2C = 273.15


class TestRainOnFrozenGround():
    nc_pr = os.path.join(TESTS_DATA, 'NRCANdaily', 'nrcan_canada_daily_pr_1990.nc')
    nc_tasmax = os.path.join(TESTS_DATA, 'NRCANdaily', 'nrcan_canada_daily_tasmax_1990.nc')
    nc_tasmin = os.path.join(TESTS_DATA, 'NRCANdaily', 'nrcan_canada_daily_tasmin_1990.nc')

    def test_3d_data_with_nans(self):
        pr = xr.open_dataset(self.nc_pr).pr
        prMM = pr.copy()
        prMM.values *= 86400.
        prMM.attrs['units'] = 'mm/day'

        tasmax = xr.open_dataset(self.nc_tasmax).tasmax
        tasmin = xr.open_dataset(self.nc_tasmin).tasmin
        tas = 0.5 * (tasmax + tasmin)
        tas.attrs = tasmax.attrs
        tasC = tas.copy()
        tasC.values -= K2C

        prMM.values[10, 1, 0] = np.nan
        pr.values[10, 1, 0] = np.nan

        out1 = precip.rain_on_frozen_ground_days(pr, tas, freq='MS')
        out2 = precip.rain_on_frozen_ground_days(prMM, tas, freq='MS')
        out3 = precip.rain_on_frozen_ground_days(prMM, tasC, freq='MS')
        out4 = precip.rain_on_frozen_ground_days(pr, tasC, freq='MS')
        pr.attrs['units'] = 'kg m-2 s-1'
        out5 = precip.rain_on_frozen_ground_days(pr, tas, freq='MS')
        out6 = precip.rain_on_frozen_ground_days(pr, tasC, freq='MS')
        np.testing.assert_array_equal(out1, out2, out3, out4)
        np.testing.assert_array_equal(out1, out5, out6)

        assert (np.isnan(out1.values[0, 1, 0]))

        assert (np.isnan(out1.values[0, -1, -1]))

        # synthetic data
        tas1 = tas[0:31, 47, 8] * 0 + K2C - 1
        tas1.attrs = tas.attrs
        pr1 = pr[0:31, 47, 8] * 0 + 25
        pr1.attrs = pr.attrs
        tas1[10] += 5
        tas1[20] += 5

        rfrz = precip.rain_on_frozen_ground_days(pr1, tas1, freq='MS')

        np.testing.assert_array_equal(rfrz, 2)


class TestPrecipAccumulation():
    # TODO: replace by fixture
    nc_file = os.path.join(TESTS_DATA, 'NRCANdaily', 'nrcan_canada_daily_pr_1990.nc')

    def test_3d_data_with_nans(self):
        # test with 3d data
        pr = xr.open_dataset(self.nc_file).pr
        prMM = xr.open_dataset(self.nc_file).pr
        prMM.values *= 86400.
        prMM.attrs['units'] = 'mm/day'
        # put a nan somewhere
        prMM.values[10, 1, 0] = np.nan
        pr.values[10, 1, 0] = np.nan

        out1 = precip.precip_accumulation(pr, freq='MS')
        out2 = precip.precip_accumulation(prMM, freq='MS')

        # test kg m-2 s-1
        pr.attrs['units'] = 'kg m-2 s-1'
        out3 = precip.precip_accumulation(pr, freq='MS')

        np.testing.assert_array_equal(out1, out2, out3)

        # check some vector with and without a nan
        x1 = prMM[:31, 0, 0].values

        prTot = x1.sum()

        assert (prTot == out1.values[0, 0, 0])

        assert (np.isnan(out1.values[0, 1, 0]))

        assert (np.isnan(out1.values[0, -1, -1]))


class TestWetDays():
    # TODO: replace by fixture
    nc_file = os.path.join(TESTS_DATA, 'NRCANdaily', 'nrcan_canada_daily_pr_1990.nc')

    def test_3d_data_with_nans(self):
        # test with 3d data
        pr = xr.open_dataset(self.nc_file).pr
        prMM = xr.open_dataset(self.nc_file).pr
        prMM.values *= 86400.
        prMM.attrs['units'] = 'mm/day'
        # put a nan somewhere
        prMM.values[10, 1, 0] = np.nan
        pr.values[10, 1, 0] = np.nan
        pr_min = 5
        out1 = precip.wetdays(pr, thresh=pr_min, freq='MS')
        out2 = precip.wetdays(prMM, thresh=pr_min, freq='MS')

        # test kg m-2 s-1
        pr.attrs['units'] = 'kg m-2 s-1'
        out3 = precip.wetdays(pr, thresh=pr_min, freq='MS')

        np.testing.assert_array_equal(out1, out2, out3)

        # check some vector with and without a nan
        x1 = prMM[:31, 0, 0].values

        wd1 = ((x1 >= pr_min) * 1).sum()

        assert (wd1 == out1.values[0, 0, 0])

        assert (np.isnan(out1.values[0, 1, 0]))

        # make sure that vector with all nans gives nans whatever skipna
        assert (np.isnan(out1.values[0, -1, -1]))
        # assert (np.isnan(wds.values[0, -1, -1]))


class TestDailyIntensity():
    # testing of wet_day and daily_pr_intensity, both are related

    nc_file = os.path.join(TESTS_DATA, 'NRCANdaily', 'nrcan_canada_daily_pr_1990.nc')

    def test_3d_data_with_nans(self):
        # test with 3d data
        pr = xr.open_dataset(self.nc_file).pr
        prMM = xr.open_dataset(self.nc_file).pr
        prMM.values *= 86400.
        prMM.attrs['units'] = 'mm/day'
        # put a nan somewhere
        prMM.values[10, 1, 0] = np.nan
        pr.values[10, 1, 0] = np.nan

        # compute with both skipna options
        pr_min = 2.
        # dis = daily_pr_intensity(pr, pr_min=pr_min, freq='MS', skipna=True)

        out1 = precip.daily_pr_intensity(pr, thresh=pr_min, freq='MS')
        out2 = precip.daily_pr_intensity(prMM, thresh=pr_min, freq='MS')

        # test kg m-2 s-1
        pr.attrs['units'] = 'kg m-2 s-1'
        out3 = precip.daily_pr_intensity(pr, thresh=pr_min, freq='MS')

        np.testing.assert_array_equal(out1, out2, out3)

        x1 = prMM[:31, 0, 0].values

        di1 = x1[x1 >= pr_min].mean()
        # buffer = np.ma.masked_invalid(x2)
        # di2 = buffer[buffer >= pr_min].mean()

        assert (np.allclose(di1, out1.values[0, 0, 0]))
        # assert (np.allclose(di1, dis.values[0, 0, 0]))
        assert (np.isnan(out1.values[0, 1, 0]))
        # assert (np.allclose(di2, dis.values[0, 1, 0]))
        assert (np.isnan(out1.values[0, -1, -1]))
        # assert (np.isnan(dis.values[0, -1, -1]))


class TestMax1Day():
    # testing of wet_day and daily_pr_intensity, both are related

    nc_file = os.path.join(TESTS_DATA, 'NRCANdaily', 'nrcan_canada_daily_pr_1990.nc')

    def test_3d_data_with_nans(self):
        # test with 3d data
        pr = xr.open_dataset(self.nc_file).pr
        prMM = xr.open_dataset(self.nc_file).pr
        prMM.values *= 86400.
        prMM.attrs['units'] = 'mm/day'
        # put a nan somewhere
        prMM.values[10, 1, 0] = np.nan
        pr.values[10, 1, 0] = np.nan

        out1 = precip.max_1day_precipitation_amount(pr, freq='MS')
        out2 = precip.max_1day_precipitation_amount(prMM, freq='MS')

        # test kg m-2 s-1
        pr.attrs['units'] = 'kg m-2 s-1'
        out3 = precip.max_1day_precipitation_amount(pr, freq='MS')

        np.testing.assert_array_equal(out1, out2, out3)

        x1 = prMM[:31, 0, 0].values
        rx1 = x1.max()

        assert (np.allclose(rx1, out1.values[0, 0, 0]))
        # assert (np.allclose(di1, dis.values[0, 0, 0]))
        assert (np.isnan(out1.values[0, 1, 0]))
        # assert (np.allclose(di2, dis.values[0, 1, 0]))
        assert (np.isnan(out1.values[0, -1, -1]))
        # assert (np.isnan(dis.values[0, -1, -1]))


class TestMaxNDay():
    # testing of wet_day and daily_pr_intensity, both are related

    nc_file = os.path.join(TESTS_DATA, 'NRCANdaily', 'nrcan_canada_daily_pr_1990.nc')

    def test_3d_data_with_nans(self):
        # test with 3d data
        pr = xr.open_dataset(self.nc_file).pr
        prMM = xr.open_dataset(self.nc_file).pr
        prMM.values *= 86400.
        prMM.attrs['units'] = 'mm/day'
        # put a nan somewhere
        prMM.values[10, 1, 0] = np.nan
        pr.values[10, 1, 0] = np.nan
        wind = 3
        out1 = precip.max_n_day_precipitation_amount(pr, window=wind, freq='MS')
        out2 = precip.max_n_day_precipitation_amount(prMM, window=wind, freq='MS')

        # test kg m-2 s-1
        pr.attrs['units'] = 'kg m-2 s-1'
        out3 = precip.max_n_day_precipitation_amount(pr, window=wind, freq='MS')

        np.testing.assert_array_equal(out1, out2, out3)

        x1 = prMM[:31, 0, 0].values
        df = pd.DataFrame({'pr': x1})
        rx3 = df.rolling(wind).sum().max()

        assert (np.allclose(rx3, out1.values[0, 0, 0]))

        assert (np.isnan(out1.values[0, 1, 0]))

        assert (np.isnan(out1.values[0, -1, -1]))


class TestMaxConsecWetDays():
    # TODO: replace by fixture
    nc_file = os.path.join(TESTS_DATA, 'NRCANdaily', 'nrcan_canada_daily_pr_1990.nc')

    def test_3d_data_with_nans(self):
        # test with 3d data
        pr = xr.open_dataset(self.nc_file).pr
        prMM = xr.open_dataset(self.nc_file).pr
        prMM.values *= 86400.
        prMM.attrs['units'] = 'mm/day'
        # put a nan somewhere
        prMM.values[10, 1, 0] = np.nan
        pr.values[10, 1, 0] = np.nan
        pr_min = 5
        out1 = precip.maximum_consecutive_wet_days(pr, thresh=pr_min, freq='MS')
        out2 = precip.maximum_consecutive_wet_days(prMM, thresh=pr_min, freq='MS')

        # test kg m-2 s-1
        pr.attrs['units'] = 'kg m-2 s-1'
        out3 = precip.maximum_consecutive_wet_days(pr, thresh=pr_min, freq='MS')

        np.testing.assert_array_equal(out1, out2, out3)

        # check some vector with and without a nan
        x1 = prMM[:31, 0, 0] * 0.
        x1[5:10] = 10
        x1.attrs['units'] = 'mm/day'
        cwd1 = precip.maximum_consecutive_wet_days(x1, freq='MS')

        assert (cwd1 == 5)

        assert (np.isnan(out1.values[0, 1, 0]))

        # make sure that vector with all nans gives nans whatever skipna
        assert (np.isnan(out1.values[0, -1, -1]))
        # assert (np.isnan(wds.values[0, -1, -1]))


class TestMaxConsecDryDays():
    # TODO: replace by fixture
    nc_file = os.path.join(TESTS_DATA, 'NRCANdaily', 'nrcan_canada_daily_pr_1990.nc')

    def test_3d_data_with_nans(self):
        # test with 3d data
        pr = xr.open_dataset(self.nc_file).pr
        prMM = xr.open_dataset(self.nc_file).pr
        prMM.values *= 86400.
        prMM.attrs['units'] = 'mm/day'
        # put a nan somewhere
        prMM.values[10, 1, 0] = np.nan
        pr.values[10, 1, 0] = np.nan
        pr_min = 5
        out1 = precip.maximum_consecutive_dry_days(pr, thresh=pr_min, freq='MS')
        out2 = precip.maximum_consecutive_dry_days(prMM, thresh=pr_min, freq='MS')

        # test kg m-2 s-1
        pr.attrs['units'] = 'kg m-2 s-1'
        out3 = precip.maximum_consecutive_dry_days(pr, thresh=pr_min, freq='MS')

        np.testing.assert_array_equal(out1, out2, out3)

        # check some vector with and without a nan
        x1 = prMM[:31, 0, 0] * 0. + 50.0
        x1[5:10] = 0
        x1.attrs['units'] = 'mm/day'
        cdd1 = precip.maximum_consecutive_dry_days(x1, freq='MS')

        assert (cdd1 == 5)

        assert (np.isnan(out1.values[0, 1, 0]))

        # make sure that vector with all nans gives nans whatever skipna
        assert (np.isnan(out1.values[0, -1, -1]))
        # assert (np.isnan(wds.values[0, -1, -1]))