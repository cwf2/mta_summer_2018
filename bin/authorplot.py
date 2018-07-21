# plot one author

l = 'vergil'

# create figure, canvas
fig = pyplot.figure(figsize=(8,5))
ax = fig.add_axes([.1,.1,.8,.8])
ax.set_title('Python - {}'.format(l))
ax.set_xlabel('PC1')
ax.set_ylabel('PC2')

# plot each author as a separate series
ax.plot(pca[labels==l,0], pca[labels==l,1], ls='', marker='')

for x, y, loc in zip(pca[labels==l,0], pca[labels==l,1], loci[labels==l]):
    ax.text(x, y, loc, fontsize=8)
fig.savefig('plot_py_{}.pdf'.format(l))
