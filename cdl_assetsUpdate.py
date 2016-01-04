
import argparse
import os
import sys
      
def main():       
    asset_version = args.verbosity

    path_str = '/jobs/hec/publish/versions/assets/massive/agents/asset_army/' 
    path_str2 = '/cdl/asset_army.cdl'

    assetsPath = path_str + str(asset_version) + path_str2
    
    print "Assets path is :", assetsPath
    current_directory = os.getcwd()
        
    currentCDL =  current_directory.split('/')[-2]
    current_to_old_CDL = currentCDL + "_old.cdl"

    currentCDL = currentCDL + ".cdl"   
    
    addCDL = "/cdl/"
    changeDirectory = current_directory + addCDL
    
    os.chdir (changeDirectory)    

    str1 = str(os.getcwd()) + "/"
    
    currentAgentPath =  str1 + str(currentCDL)     
    
    formation_buffer, asset_begin, asset_end, segment_root, fuzzy, tot_number_lines  = currentAgent(currentAgentPath)
    
    asset_buffer, asset_begin2, asset_end2, segment_root2, fuzzy2 = assetAgent(assetsPath)  

    final_buffer = appendAssets(formation_buffer, asset_buffer, asset_begin, asset_begin2, asset_end2, asset_end, segment_root, segment_root2, fuzzy2, fuzzy, tot_number_lines )
   
    diff1 = asset_end2 - asset_begin2   
    diff2 = segment_root - asset_end    
    diff3 = fuzzy2 - segment_root2    
    diff4 = tot_number_lines - fuzzy     
        
    print_lines = asset_begin + diff1 + diff2 + diff3 + diff4     

    cdlFilePath2 = currentAgentPath

    rename_file(currentCDL, current_to_old_CDL)

    fo = open(cdlFilePath2, "w") 
    for i in range (0, print_lines):
	fo.write(final_buffer[i])
    fo.close() 

 
def rename_file(currentCDL, current_to_old_CDL):    
    os.rename(currentCDL, current_to_old_CDL)   
       

def currentAgent(currentAgentPath):
    formation_buffer = []
    with open(currentAgentPath, 'r') as f:
        line_number = 0
        for line in f.readlines():
            line_number = line_number + 1
            
            if line.startswith('        variable A_S_S_E_T___BEGIN'):             
                currentAgent_asset_begin = line_number                          
                        
            if line.startswith('        variable A_S_S_E_T___END'):             
                currentAgent_asset_end = line_number            
                            
            if line.startswith('segment root'): 
                currentAgent_segment_root = line_number                
                
            if line.startswith('fuzzy'): 
                currentAgent_fuzzy = line_number                
                break
                
        
    with open(currentAgentPath, 'r') as f:
        number_of_lines = 0
        for line in f.readlines():
            formation_buffer.append(line)
            number_of_lines = number_of_lines + 1
            
        tot_number_lines = number_of_lines
            
    return formation_buffer, currentAgent_asset_begin, currentAgent_asset_end, currentAgent_segment_root, currentAgent_fuzzy, tot_number_lines

##-----------Assets -----------------------##
    
def assetAgent(assetsPath):    
    asset_buffer = []
    with open(assetsPath, 'r') as f:
        asset_line_number  = 0
        variable_line_count = 0
        for line in f.readlines():
            asset_line_number = asset_line_number + 1
            asset_buffer.append(line)
            if line.startswith('        variable'):
                #print line
                #variable_buffer.append(line)
                variable_line_count = variable_line_count + 1                      
            if line.startswith('        variable A_S_S_E_T___BEGIN'):     
                assetAgent_asset_begin = asset_line_number   
		                                
            if line.startswith('        variable A_S_S_E_T___END'):      
                assetAgent_asset_end = asset_line_number    
                                 
            if line.startswith('segment root'):      
                assetAgent_segment_root = asset_line_number    
                                
            if line.startswith('fuzzy'):      
                assetAgent_fuzzy = asset_line_number    
                break                                                       
	f.close()

    return asset_buffer, assetAgent_asset_begin, assetAgent_asset_end, assetAgent_segment_root, assetAgent_fuzzy
           
##-------------  printing into a file --------------------##
	
def appendAssets(formation_buffer, asset_buffer, currentAgent_asset_begin, assetAgent_asset_begin, assetAgent_asset_end, currentAgent_asset_end, currentAgent_segment_root, assetAgent_segment_root, assetAgent_fuzzy, currentAgent_fuzzy, tot_number_lines ):
    
    final_buffer = []
    for i in range (0,currentAgent_asset_begin-1):
        final_buffer.append(formation_buffer[i])                     
    
    for i in range (assetAgent_asset_begin-1, assetAgent_asset_end):        
        final_buffer.append(asset_buffer[i])              
            
    for i in range (currentAgent_asset_end, currentAgent_segment_root-1):        
        final_buffer.append(formation_buffer[i])          
      
    for i in range (assetAgent_segment_root-1, assetAgent_fuzzy-1):        
        final_buffer.append(asset_buffer[i])        
        
    for i in range (currentAgent_fuzzy -1, tot_number_lines):        
        final_buffer.append(formation_buffer[i])                
        
    return final_buffer

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbosity", help="Asset version")
    args = parser.parse_args()
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbosity", help="Asset version")
    args = parser.parse_args()
   
    if args.verbosity:
        print "Asset version is :", args.verbosity
    else:
        print "Please enter a valid Assets version !!"
        raise
    main()
  
    

    
    
