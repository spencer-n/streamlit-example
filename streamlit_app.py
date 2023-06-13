import streamlit as st
import gdal
from osgeo import osr
import tempfile
import shutil

# Target spatial reference system (WGS84, EPSG:4326)
target_epsg = 4326

# Function to reproject the DEM file
def reproject_dem(input_file):
    # Create a temporary directory to store intermediate files
    temp_dir = tempfile.mkdtemp()
    
    # Get the filename and extension of the input file
    filename = input_file.name
    extension = filename.split(".")[-1]

    # Path to the temporary input DEM file
    temp_input_file = os.path.join(temp_dir, filename)

    # Copy the uploaded file to the temporary directory
    with open(temp_input_file, "wb") as f:
        f.write(input_file.getbuffer())

    # Path to the output reprojected DEM file
    output_file = os.path.join(temp_dir, "reprojected_dem.tif")

    # Open the input DEM file
    dataset = gdal.Open(temp_input_file)

    # Get the spatial reference system of the input DEM
    source_srs = osr.SpatialReference()
    source_srs.ImportFromWkt(dataset.GetProjection())

    # Create a transformation from the source to the target spatial reference system
    transform = osr.CoordinateTransformation(source_srs, osr.SpatialReference(target_epsg))

    # Get the input DEM's dimensions
    width = dataset.RasterXSize
    height = dataset.RasterYSize

    # Get the geotransformation information (bounding box and pixel size) of the input DEM
    geotransform = dataset.GetGeoTransform()

    # Create an output dataset with the reprojected DEM
    driver = gdal.GetDriverByName("GTiff")
    output_dataset = driver.Create(output_file, width, height, 1, gdal.GDT_Float32)

    # Set the geotransformation and projection information for the output dataset
    output_dataset.SetGeoTransform(geotransform)
    output_dataset.SetProjection(target_epsg)

    # Reproject each pixel of the input DEM to the target spatial reference system
    gdal.ReprojectImage(dataset, output_dataset, source_srs.ExportToWkt(), transform.ExportToWkt(), gdal.GRA_Bilinear)

    # Close the datasets
    dataset = None
    output_dataset = None

    # Remove the temporary input DEM file
    os.remove(temp_input_file)

    return output_file

# Create the Streamlit app
def main():
    st.title("DEM Reprojection")

    # Upload the input DEM file
    input_file = st.file_uploader("Upload DEM file", type=["tif", "tiff"])

    if input_file is not None:
        # Display the uploaded DEM file
        st.subheader("Input DEM")
        st.image(input_file)

        # Reproject the DEM file
        reprojected_file = reproject_dem(input_file)

        # Display the reprojected DEM file
        st.subheader("Reprojected DEM")
        st.image(reprojected_file)

        # Remove the temporary directory
        shutil.rmtree(os.path.dirname(reprojected_file))

# Run the Streamlit app
if __name__ == "__main__":
    main()
