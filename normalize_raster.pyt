import arcpy
import os
from arcpy.sa import *

class Toolbox:
    def __init__(self):
        """Define the toolbox."""
        self.label = "Normalization Toolbox"
        self.alias = "Normalization"
        self.tools = [NormalizeRasterSimple]

class NormalizeRasterSimple:
    def __init__(self):
        """Define the tool."""
        self.label = "Normalize Raster (Simple)"
        self.description = "Normalize raster to 0-1 range using (value - min)/(max - min)"
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""
        params = []
        
        # Input raster
        input_param = arcpy.Parameter(
            name="in_raster",
            displayName="Input Raster",
            datatype=["GPRasterLayer", "DERasterDataset"],
            parameterType="Required",
            direction="Input")
        params.append(input_param)
        
        # Output raster
        output_param = arcpy.Parameter(
            name="out_raster",
            displayName="Output Raster",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Output")
        params.append(output_param)
        
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify parameter values and properties."""
        # Auto-generate output name
        if parameters[0].value and not parameters[1].altered:
            in_raster = parameters[0].valueAsText
            base_name = os.path.splitext(os.path.basename(in_raster))[0]
            workspace = arcpy.env.workspace or os.path.dirname(in_raster)
            parameters[1].value = os.path.join(workspace, f"{base_name}_normalized")
        return

    def execute(self, parameters, messages):
        """Execute the tool."""
        arcpy.env.overwriteOutput = True
        
        input_raster = parameters[0].valueAsText
        output_raster = parameters[1].valueAsText
        
        arcpy.AddMessage(f"Input raster: {input_raster}")
        
        try:
            # Get raster properties
            min_val_str = arcpy.GetRasterProperties_management(input_raster, "MINIMUM").getOutput(0)
            max_val_str = arcpy.GetRasterProperties_management(input_raster, "MAXIMUM").getOutput(0)
            
            # Handle comma as decimal separator
            min_val = float(min_val_str.replace(',', '.'))
            max_val = float(max_val_str.replace(',', '.'))
            
            arcpy.AddMessage(f"Minimum value: {min_val}")
            arcpy.AddMessage(f"Maximum value: {max_val}")
            
            # Check for constant raster
            if max_val == min_val:
                arcpy.AddMessage("Constant raster - setting all values to 0.5")
                normalized = Con(Raster(input_raster) >= min_val, 0.5, 0.5)
            else:
                # Apply normalization formula using Raster Calculator
                arcpy.AddMessage("Applying normalization formula: (value - min) / (max - min)")
                normalized = (Raster(input_raster) - min_val) / (max_val - min_val)
            
            # Save the result
            normalized.save(output_raster)
            
            arcpy.AddMessage(f"Output saved to: {output_raster}")
            
            # Calculate statistics
            arcpy.management.CalculateStatistics(output_raster)
            
            # Verify the output
            out_min = float(arcpy.GetRasterProperties_management(output_raster, "MINIMUM").getOutput(0))
            out_max = float(arcpy.GetRasterProperties_management(output_raster, "MAXIMUM").getOutput(0))
            
            arcpy.AddMessage(f"Verification - Output range: {out_min:.6f} to {out_max:.6f}")
            
            arcpy.SetParameterAsText(1, output_raster)
            
        except Exception as e:
            arcpy.AddError(f"Error: {str(e)}")
            raise

# For standalone testing
if __name__ == "__main__":
    # Test the function
    input_raster = r"C:\Your\Input\Raster.tif"
    output_raster = r"C:\Your\Output\Normalized.tif"
    
    # Create toolbox instance
    tool = NormalizeRasterSimple()
    
    # Run normalization
    arcpy.env.overwriteOutput = True
    arcpy.AddMessage("Starting normalization...")
    
    # Get min and max
    min_val = float(arcpy.GetRasterProperties_management(input_raster, "MINIMUM").getOutput(0))
    max_val = float(arcpy.GetRasterProperties_management(input_raster, "MAXIMUM").getOutput(0))
    
    arcpy.AddMessage(f"Min: {min_val}, Max: {max_val}")
    
    # Calculate normalized raster
    normalized = (Raster(input_raster) - min_val) / (max_val - min_val)
    normalized.save(output_raster)
    
    arcpy.AddMessage(f"Normalization complete. Output: {output_raster}")