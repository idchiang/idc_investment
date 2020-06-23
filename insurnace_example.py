# -*- coding: utf-8 -*-
"""
Created on Sat Jun 20 21:36:59 2020

@author: I-Da Chiang
"""
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt


def read_data(diffs=[]):
    # columns: ['Strike', 'Price', 'Expiration', 'IV', 'Delta', 'Theta',
    #           'Delta_round', 'Price_30d']
    df = pd.read_csv('data/put_table.csv', comment='#')
    
    for diff in diffs:
        col = [np.nan] * len(df)
        for i, strike in enumerate(df['Strike']):
            temp = df[(df['Strike'] == (strike - diff)) &
                      (df['Expiration'] == df['Expiration'][i])]
            if len(temp) > 0:
                col[i] = temp['Price_30d'].values[0]
        df[diff] = col
    return df


def make_images(initial_price=195.0, diffs=[], doPlotDelta=True, doPlotTime=True, doPlotIV=True):
    df = read_data(diffs=diffs)
    no_insurance = [100.0 * diff / initial_price for diff in diffs]
    cmap = mpl.cm.jet
    colors = cmap(np.linspace(0, 1, 1000))
    #
    if doPlotDelta:
        fig, ax = plt.subplots(2, 3, figsize=(24, 12))
        for j, fixedDelta in enumerate([-0.1, -0.2, -0.3, -0.4, -0.5]):
            p, q = j // 3, j % 3
            mask = df['Delta_round'] == fixedDelta
            for ind in df[mask].index:
                dfi = df.iloc[ind]
                raw = initial_price + dfi['Price']
                prices_30d = [np.nan] * len(diffs)
                for i, diff in enumerate(diffs):
                    prices_30d[i] = \
                        100.0 * (max(initial_price + diff + dfi[diff], dfi['Strike']) -
                                 raw) / raw
                label = '$' + str(int(dfi['Strike'])) + ' Exp' + \
                    str(int(dfi['Expiration'])) + ' IV' + \
                    str(round(dfi['IV'], 2))
                ax[p, q].plot(diffs, prices_30d, label=label)
            ax[p, q].plot(diffs, no_insurance, 'k--', label='No insurance')
            ax[p, q].legend(fontsize=10)
            ax[p, q].grid()
            if (q == 0):
                ax[p, q].set_ylabel('Change in total value (%)', size=18)
            if (p == 1) or (q == 2):
                ax[p, q].set_xlabel('Change in underlying value ($)', size=18)
            ax[p, q].set_title('delta~' + str(round(fixedDelta, 1)), size=20)
        ax[-1, -1].axis('off')
        fig.suptitle('Initial price=$' + str(initial_price) +
                     '; Estimated for 30 days', size=24)
        fig.savefig('examples/byDelta.png')
        #
        fig, ax = plt.subplots(figsize=(16, 12))
        norm = mpl.colors.Normalize(vmin=np.min(df['Delta']),
                                    vmax=np.max(df['Delta']))
        for ind in df.index:
            dfi = df.iloc[ind]
            raw = initial_price + dfi['Price']
            prices_30d = [np.nan] * len(diffs)
            for i, diff in enumerate(diffs):
                prices_30d[i] = \
                    100.0 * (max(initial_price + diff + dfi[diff], dfi['Strike']) -
                             raw) / raw
            ax.plot(diffs, prices_30d,
                    color=colors[int(np.interp(dfi['Delta'],
                                               [np.min(df['Delta']),
                                                np.max(df['Delta'])],
                                               [0, 999]))])
        ax.plot(diffs, no_insurance, 'k--', label='No insurance')
        ax.grid()
        plt.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax,
                     label='delta')
        ax.set_ylabel('Change in total value (%)', size=18)
        ax.set_xlabel('Change in underlying value ($)', size=18)
        fig.suptitle('Initial price=$' + str(initial_price) +
                     '; Estimated for 30 days', size=24)
        fig.savefig('examples/byDeltaAIO.png')
    #
    if doPlotTime:
        fig, ax = plt.subplots(figsize=(16, 12))
        norm = mpl.colors.Normalize(vmin=np.min(df['Expiration']),
                                    vmax=np.max(df['Expiration']))
        for ind in df[df['Delta_round'] == -0.3].index:
            dfi = df.iloc[ind]
            raw = initial_price + dfi['Price']
            prices_30d = [np.nan] * len(diffs)
            for i, diff in enumerate(diffs):
                prices_30d[i] = \
                    100.0 * (max(initial_price + diff + dfi[diff], dfi['Strike']) -
                             raw) / raw
            ax.plot(diffs, prices_30d,
                    color=colors[int(np.interp(dfi['Expiration'],
                                               [np.min(df['Expiration']),
                                                np.max(df['Expiration'])],
                                               [0, 999]))])
        ax.plot(diffs, no_insurance, 'k--', label='No insurance')
        ax.grid()
        plt.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax,
                     label='Expiration (+Month)')
        ax.set_ylabel('Change in total value (%)', size=18)
        ax.set_xlabel('Change in underlying value ($)', size=18)
        title = 'Initial price=$' + str(initial_price) + \
            '; Estimated for 30 days; Delta ~ -0.3'
        ax.set_title(title, size=24)
        fig.savefig('examples/byExpirationAIO.png')
    #
    if doPlotIV:
        fig, ax = plt.subplots(figsize=(16, 12))
        norm = mpl.colors.Normalize(vmin=np.min(df['Expiration']),
                                    vmax=np.max(df['Expiration']))
        ax.scatter(df['Delta'], df['IV'],
                   c=[colors[int(c)] for c in
                      np.interp(df['Expiration'],
                                [np.min(df['Expiration']),
                                 np.max(df['Expiration'])],
                                [0, 999])])
        ax.grid()
        plt.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax,
                     label='Expiration (+Month)')
        ax.set_ylabel('IV', size=18)
        ax.set_xlabel('Delta', size=18)
        fig.savefig('examples/IV_to_delta.png')


if __name__ == '__main__':
    # sorry, these two are currently hard-coded.
    initial_price = 195.0
    diffs = np.arange(-40, 45, 5)
    make_images(initial_price=initial_price,
                diffs=diffs,
                doPlotDelta=False,
                doPlotTime=True,
                doPlotIV=True
                )
