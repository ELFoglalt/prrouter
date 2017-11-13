doc = app.activeDocument

llet = 'ABCDEFGHIJLKM'.split("")
lnum = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13']

gridset = doc.layerSets.getByName("InlineGrid").artLayers

for (l=0; l < llet.length; ++l)
for (n=0; n < lnum.length; ++n)
{
    layer = gridset.getByName(llet[l] + lnum[n])
    layer.translate(l*300, n*300)
}