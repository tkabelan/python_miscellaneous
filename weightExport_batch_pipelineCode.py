import os
import maya.cmds as cmds

def getPathToWeightsDir():
    return getPath(fileMode = 3, fileFilter = "Massive Weight File (*.w)", okCaption = "Select Folder")

def getPath(fileMode = 0, fileFilter = "", okCaption = None):
    job = os.getenv("JOB")
    startPath = "/jobs/%s/publish/versions/massive/" % job

    result = cmds.fileDialog2(startingDirectory=startPath, fileMode=fileMode, fileFilter=fileFilter, okCaption = okCaption)
    return result[0] if result else None

def getSelection():
    sel = cmds.ls(selection=True)
    return sel

def gatherVertexDeformerInfo(weightFilePath):
    with open(weightFilePath, 'r') as f:
        deformers = {}
        vertices = {}
        for line in f.readlines():
            line = line.rstrip("\n")
            if line and not line.startswith("#"):
                if (line.startswith("deformer")):
                    # deformer line
                    splitStr = line.split()
                    deformerId = splitStr[1]
                    deformerName = splitStr[2]
                    deformers[deformerId] = deformerName
                else:
                    # vertex line
                    vertexId, vertexDict = parseVertex(line)
                    vertices[vertexId] = vertexDict

        return deformers, vertices


def parseVertex(line):
    splitStr = line.split()

    vertexId = splitStr[0].rstrip(':')
    vertexDict = {}
    # separate deformer/weight pairs from string
    dwPairs = splitStr[1:]
    for i in range(len(dwPairs)/2):
        vertexDeformer = dwPairs[2*i]
        vertexWeight = dwPairs[2*i+1]
        vertexDict[vertexDeformer] = vertexWeight
	#--------- return dictionary ---------##
    return vertexId, vertexDict


def weightZero(skinClusterName, deformerName):
    scNormalWeights = skinClusterName + '.normalizeWeights'
    cmds.setAttr(scNormalWeights, 1)
    cmds.skinPercent(skinClusterName, transformValue=[ (deformerName, 1.0)])
    cmds.setAttr(scNormalWeights, 0)
    cmds.skinCluster(skinClusterName, edit = True, fnw = True)
    cmds.skinPercent(skinClusterName, transformValue=[ (deformerName, 0.0)])


def assignWeights(skinClusterName, objectName, vertices, deformers):
    scNormalWeights = skinClusterName + '.normalizeWeights'
    cmds.setAttr( scNormalWeights, 0)
    for vertexId in vertices:
        for deformerId in vertices[vertexId]:
            deformerVertex = "%s.vtx[%s]" % (objectName, vertexId)
            deformerName = deformers[deformerId]
            vertexWeight = float( vertices[vertexId][deformerId] )
            cmds.skinPercent( skinClusterName, deformerVertex,  transformValue=[(deformerName, vertexWeight)])


def importWeightsForObject(importDir, obj):
    shape = cmds.listRelatives(obj)
    skinCluster = cmds.listConnections( shape, t='skinCluster' )
    if not skinCluster:
        print "WARNING: No skinCluster in object", obj
        return
       ### return string instead of list
    skinClusterName = ''.join(skinCluster)
	##--- obj 
    objName = str(obj)

    # read file
    weightFilePath = os.path.join(importDir, "%s.w" % objName)
    if not os.path.exists(weightFilePath):
        print "WARNING: No weight file found for object", obj
        return
        
    print "skinCluster & weight file :", skinClusterName, weightFilePath
    deformers, vertices = gatherVertexDeformerInfo(weightFilePath)

    # apply weights
    for deformerName in deformers.values():
        weightZero(skinClusterName, deformerName)
    print "Assigning Zero Weights for %s done." % skinClusterName

    assignWeights(skinClusterName, objName, vertices, deformers)
    print "Weights imported for %s -> %s" % (objName, skinClusterName)


def importWeights():
    importDir = getPathToWeightsDir()

    selection = getSelection()
    if not selection:
        raise ValueError ("Please select skinned geometry")

    for obj in selection:
        importWeightsForObject(importDir, obj)

if __name__ == "__main__": 
    importWeights()
