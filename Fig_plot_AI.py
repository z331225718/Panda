from matplotlib import pyplot as plt
from matplotlib.pyplot import subplots
from numpy import linspace, ones, log10, max, min, argmax, argmin, zeros, around, all
from skrf import Network


def plot_data_init(ax, x, y, labels):
    ax1d = ax.flatten()
    i = 0
    keys = list(y.keys())
    for axs in ax1d:
        axs.plot(x, y[keys[i]].T)
        axs.set_xlabel('Freq (GHz)')
        axs.set_ylabel('dB')
        axs.set_title(keys[i])
        axs.legend(labels[i])
        axs.grid()
        i = i+1


def plot_mask(ax, x, y):
    for axs in ax:
        for i in range(len(x)):
            axs.plot(x[i], y[i], linestyle='--', color='k', linewidth=2)


def plot_point(ax, y, freq_range, df, op='max'):
    values = list(y.values())
    for i in range(len(ax)):
        if op == 'max':
            Plot_Data = max([max(row) for row in values[i][:lane, int(
                freq_range[0]/df):int(freq_range[1]/df)+1]])
            argf_Data = argmax([max(row) for row in values[i][:lane, int(
                freq_range[0]/df):int(freq_range[1]/df)+1]])
            arg_Data_f = df*[argmax(row) for row in values[i][:lane,
                                                              int(freq_range[0]/df):int(freq_range[1]/df)+1]][argf_Data]
        else:
            Plot_Data = min([min(row) for row in values[i][:lane, int(
                freq_range[0]/df):int(freq_range[1]/df)+1]])
            argf_Data = argmin([min(row) for row in values[i][:lane, int(
                freq_range[0]/df):int(freq_range[1]/df)+1]])
            arg_Data_f = df*[argmin(row) for row in values[i][:lane,
                                                              int(freq_range[0]/df):int(freq_range[1]/df)+1]][argf_Data]

        ax[i].scatter(arg_Data_f, Plot_Data, color='r')
        ax[i].text(arg_Data_f, Plot_Data, around(Plot_Data, decimals=2))


def save_subfig(fig, ax, save_path, fig_name):
    bbx = ax.get_tightbbox(fig.canvas.get_renderer()).expanded(1.02, 1.02)
    extent = bbx.transformed(fig.dpi_scale_trans_inverted())
    fig.savefig(save_path+fig_name, bbox_inches=extent)


# figure1 RL & IL
Data = Network('/example/Host_diff_ntwk.ntwk')
lane = 8
df = Data.frequency.df_scaled[0]

# 初始化Data
Params_to_show = ['HTX_RL', 'HRX_RL', 'HTX_IL', 'HRX_IL', 'HTX_CC_RL',
                  'HRX_CC_RL', 'HTX_DC_RL', 'HRX_DC_RL', 'HTX_FEXT', 'HRX_FEXT', 'Host_NEXT']
Results_to_show = [zeros((lane, len(Data.f)))
                   for _ in range(len(Params_to_show)-3)]
Data_dict = dict(zip(Params_to_show[0:8], Results_to_show))
Results_to_show_xtalk = [zeros((lane*lane, len(Data.f))) for _ in range(3)]
Data_dict_xtalk = dict(zip(Params_to_show[8:], Results_to_show_xtalk))
Data_dict.update(Data_dict_xtalk)
HTX_label = ['HTX' + str(i) for i in range(1, lane+1)]
HRX_label = ['HRX' + str(i) for i in range(1, lane+1)]
legend_HTX_FEXT = []
legend_HRX_FEXT = []
legend_Host_NEXT = []
for i in range(lane):
    for j in range(lane):
        if i != j:
            Data_dict['HTX_FEXT'][i*lane+j] = 20 * \
                log10(abs(Data.s[:, 2*i, 2*j+1]))
            legend_HTX_FEXT.append(HTX_label[i]+'_'+HTX_label[j])
            Data_dict['HRX_FEXT'][i*lane+j] = 20 * \
                log10(abs(Data.s[:, 2*(i+lane), 2*(j+lane)+1]))
            legend_HRX_FEXT.append(HRX_label[i]+'_'+HRX_label[j])
        Data_dict['Host_NEXT'][i*lane+j] = 20 * \
            log10(abs(Data.s[:, 2*i, 2*(i+lane)+1]))
        legend_Host_NEXT.append(HTX_label[i]+'_'+HRX_label[j])
    Data_dict['HTX_RL'][i] = 20*log10(abs(Data.s[:, 2*i+1, 2*i+1]))
    Data_dict['HRX_RL'][i] = 20 * \
        log10(abs(Data.s[:, 2*(i+lane)+1, 2*(i+lane)+1]))
    Data_dict['HTX_IL'][i] = 20*log10(abs(Data.s[:, 2*i, 2*i+1]))
    Data_dict['HRX_IL'][i] = 20*log10(abs(Data.s[:, 2*(i+lane), 2*(i+lane)+1]))

    Data_dict['HTX_CC_RL'][i] = 20 * \
        log10(abs(Data.s[:, 2*i+4*lane, 2*i+4*lane]))
    Data_dict['HRX_CC_RL'][i] = 20 * \
        log10(abs(Data.s[:, 2*(i+lane)+4*lane, 2*(i+lane)+4*lane]))
    Data_dict['HTX_DC_RL'][i] = 20*log10(abs(Data.s[:, 2*i, 2*i+4*lane]))
    Data_dict['HRX_DC_RL'][i] = 20 * \
        log10(abs(Data.s[:, 2*(i+lane), 2*(i+lane)+4*lane]))
Data_dict['HTX_FEXT'] = Data_dict['HTX_FEXT'][~all(
    Data_dict['HTX_FEXT'] == 0, axis=1)]
Data_dict['HRX_FEXT'] = Data_dict['HRX_FEXT'][~all(
    Data_dict['HRX_FEXT'] == 0, axis=1)]

# figure1 Diff to DIff RL and IL
fig, axs = subplots(ncols=2, nrows=2, figsize=(20, 12))
fig2, axs2 = subplots(ncols=2, nrows=2, figsize=(20, 12))
fig3, axs3 = subplots(ncols=1, nrows=3, figsize=(20, 12), sharex=True)

plot_data_init(axs, Data.f/1e9, {key: Data_dict[key] for key in Params_to_show[0:4]}, [
               HTX_label, HRX_label, HTX_label, HRX_label])
Mask_x = linspace(0, 28, int(28/df)+1)
Mask_RL = -15*ones(int(28/df)+1)
Mask_IL = -1.5*ones(int(28/df)+1)
plot_mask([axs[0, 0], axs[0, 1]], [Mask_x], [Mask_RL])
plot_point([axs[0, 0], axs[0, 1]], {key: Data_dict[key]
           for key in Params_to_show[0:2]}, [0, 28], df=df, op='max')
plot_mask([axs[1, 0], axs[1, 1]], [Mask_x], [Mask_IL])
plot_point([axs[1, 0], axs[1, 1]], {key: Data_dict[key]
           for key in Params_to_show[2:4]}, [0, 28], df=df, op='min')
fig.suptitle('Host Diff RL & IL', fontsize=30)

# figure2 Comm to Comm and Diff to Comm
plot_data_init(axs2, Data.f/1e9, {key: Data_dict[key] for key in Params_to_show[4:8]}, [
               HTX_label, HRX_label, HTX_label, HRX_label])
Mask_CC_x1 = linspace(0, 2.5, int(2.5/df)+1)
Mask_CC_RL1 = -10*ones(int(2.5/df)+1)
Mask_CC_x2 = linspace(2.5, 16, int(13.5/df)+1)
Mask_CC_RL2 = -8*ones(int(13.5/df)+1)
Mask_CC_x3 = linspace(16, 28, int(12/df)+1)
Mask_CC_RL3 = -5*ones(int(12/df)+1)

Mask_DC_x1 = linspace(0, 14, int(14/df)+1)
Mask_DC_RL1 = -24*ones(int(14/df)+1)
Mask_DC_x2 = linspace(14, 28, int(14/df)+1)
Mask_DC_RL2 = -16*ones(int(14/df)+1)
Mask_DC_x3 = linspace(28, 50, int(22/df)+1)
Mask_DC_RL3 = -10+18*log10(2*Mask_DC_x3/53.125)

plot_mask([axs2[0, 0], axs2[0, 1]], [Mask_CC_x1, Mask_CC_x2,
          Mask_CC_x3], [Mask_CC_RL1, Mask_CC_RL2, Mask_CC_RL3])
plot_mask([axs2[1, 0], axs2[1, 1]], [Mask_DC_x1, Mask_DC_x2,
          Mask_DC_x3], [Mask_DC_RL1, Mask_DC_RL2, Mask_DC_RL3])
fig2.suptitle('Host CC & DC RL', fontsize=30)

# figure3 Crosstalk
plot_data_init(axs3, Data.f/1e9, {key: Data_dict[key] for key in Params_to_show[8:]}, [
               legend_HTX_FEXT, legend_HRX_FEXT, legend_Host_NEXT])
Mask_xtalk_x = linspace(0, 28, int(28/df)+1)
Mask_FEXT_y = -50*ones(int(28/df)+1)
Mask_NEXT_y = -60*ones(int(28/df)+1)
plot_mask([axs3[0], axs3[1]], [Mask_xtalk_x], [Mask_FEXT_y])
plot_mask([axs3[2]], [Mask_xtalk_x], [Mask_NEXT_y])
plot_point([axs3[0], axs3[1], axs3[2]], {
           key: Data_dict[key] for key in Params_to_show[8:]}, [0, 28], df=df, op='max')

fig3.subplots_adjust()
fig3.suptitle('Host CrossTalk', fontsize=30)

fig.savefig('RL&IL.png')
fig2.savefig('CC&DC.png')
fig3.savefig('CrossTalk.png')

save_subfig(fig,axs[0,0],'./','HTX_Diff_RL.png')
save_subfig(fig,axs[0,1],'./','HRX_Diff_RL.png')
save_subfig(fig,axs[1,0],'./','HTX_Diff_IL.png')
save_subfig(fig,axs[1,1],'./','HRX_Diff_IL.png')

