# Load the Python Standard and DesignScript Libraries
import System
import sys
import clr
clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *
from System.Collections.Generic import *

clr.AddReference("RevitAPI")
import Autodesk
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import Transaction

clr.AddReference("RevitNodes")
import Revit
clr.ImportExtensions(Revit.GeometryConversion)
clr.ImportExtensions(Revit.Elements)

clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

clr.AddReference('DSCoreNodes')
from DSCore import *

# Get doc, uiapp and app
doc = DocumentManager.Instance.CurrentDBDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application

# input .rfa file paths
RFAfilepaths = IN[0]
# Input .sat file paths
SATfilepaths = IN[1]
SATfilepaths_name = [i[:-4] for i in SATfilepaths]

# SAT Import options
SAT_IOption = SATImportOptions()
SAT_IOption.VisibleLayersOnly = True
SAT_IOption.Placement = ImportPlacement.Origin
SAT_IOption.ColorMode = ImportColorMode.Preserved
SAT_IOption.Unit = ImportUnit.Default
# Save as options
Save_Option = SaveAsOptions()
Save_Option.OverwriteExistingFile = True
Save_Option.Compact = True
Save_Option.MaximumBackups = 1

TransactionManager.Instance.ForceCloseTransaction()

# list of updated .rfa files
updated = []

for RFAfilepath in RFAfilepaths:
	RFAfilepath_name = RFAfilepath[:-4]
	if RFAfilepath_name in SATfilepaths_name:
		# Find corresponding SAT filepath
		SATfilepath = SATfilepaths[SATfilepaths_name.index(RFAfilepath_name)]
		
		# Open .rfa file
		RFAopen = app.OpenDocumentFile(RFAfilepath)
		
		# Start transaction
		trans = Transaction(RFAopen, RFAfilepath_name)
		trans.Start()
		
		# Get all elements from open .rfa document
		collector = FilteredElementCollector(RFAopen)
		
		# delete existing elements
		allElements = collector.OfCategory(BuiltInCategory.OST_GenericModel).ToElements()
		for i in allElements:
			RFAopen.Delete(i.Id)
			
		# Import .sat file
		#RFAopen.Import(SATfilepath, SAT_IOption, view)
		shapeImporter = ShapeImporter()
		shapeImporter.InputFormat = ShapeImporterSourceFormat.SAT
		shapes = shapeImporter.Convert(RFAopen, SATfilepath)
		dsImportedSat = DirectShape.CreateElement(RFAopen, ElementId(BuiltInCategory.OST_GenericModel))
		dsImportedSat.SetShape(shapes)
		
		# Commit transaction changes
		trans.Commit()
		trans.Dispose()
		
		# Save .rfa file
		RFAopen.SaveAs(RFAfilepath, Save_Option)
		RFAopen.Close(False)
		updated.append(RFAfilepath)

#Save resulting Revit file to the destination path:
OUT = updated


