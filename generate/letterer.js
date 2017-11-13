doc = app.activeDocument

llet = 'ABCDEFGHIJLKM'.split("")
//lnum = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
lnum = [13]

letterLookup = {};
numberLookup = {};

numberLayers = doc.layerSets.getByName("Numbers").artLayers
for (j=0; j < numberLayers.length; ++j)
{
    numberLookup[numberLayers[j].name] = numberLayers[j]
}

letterLayers = doc.layerSets.getByName("Letters").artLayers
for (j=0; j < letterLayers.length; ++j)
{
    letterLookup[letterLayers[j].name] = letterLayers[j]
}

outputset = doc.layerSets.add()
outputset.name = "Grid"

for (l=0; l < llet.length; ++l)
for (n=0; n < lnum.length; ++n)
{
    set = outputset.layerSets.add()
    set.name = llet[l] + lnum[n]
    numberLookup[lnum[n]].duplicate(set, ElementPlacement.PLACEATEND)
    letterLookup[llet[l]].duplicate(set, ElementPlacement.PLACEATEND)
    set.merge()
}
