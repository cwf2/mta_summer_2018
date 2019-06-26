for hi in sorted(set(t.authors)):
    fig = plot.ACAbasePlot(xs=t.pca[:,0], ys=t.pca[:,1], labels=t.authors, hi=hi)
    fig.savefig('test_' + hi + '.png')
    fig = plot.ACAbasePlot(xs=t.pca[:,0], ys=t.pca[:,1], labels=t.authors, hi=hi, legend=True)
    fig.savefig('test_' + hi + '_leg.png')

		
		
		
def ACAbasePlot(xs, ys, labels, colors=COLORS, title=None, legend=False, hi=None):
    '''Basic plot w/ single author highlighted'''

    # if we're going to have a legend, adjust figure width to make room
    if legend and len(set(labels)) > 1:
       w = .6
    else:
       w = .8

    # create figure, canvas
    fig = pyplot.figure(figsize=(8,5))
    ax = fig.add_axes([.1, .1, w, .8])
    if title is not None:
        ax.set_title(title)
    ax.set_xlabel('PC1')
    ax.set_ylabel('PC2')

    # marker set to use
    markers = 'ovP*Xd^43p'
    
    i_hi = None
    l_hi = None

    # plot each author as a separate series
    for i, l in enumerate(sorted(set(labels))):
        if l == hi:
            color = colors[i]
            i_hi = i
            l_hi = l
        else:
            color = '#aaaaaa'
        ax.plot(xs[labels==l], ys[labels==l],
            ls='', marker=markers[i], color=color, label=l)

    if i_hi is not None:
        ax.plot(xs[labels==l_hi], ys[labels==l_hi],
            ls='', marker=markers[i_hi], color=colors[i_hi])

    # add legend
    if legend and len(set(labels)) > 1:
        fig.legend()

    return fig
