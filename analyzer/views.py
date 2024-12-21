from django.shortcuts import render
from .models import *
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os
import matplotlib
matplotlib.use('Agg')
import logging as log 

log.basicConfig(filename='test.log' , level=log.INFO , format='%(asctime)s - %(levelname)s - %(message)s ')

from django.conf import settings

def home(request):
    try :
            if(request.method == 'POST'):
                file = request.FILES.get('file')   # Get the frontend data to backend
                new_file = file

                if file:
                    file_extension = file.name.split('.')[-1].lower()
                    if file_extension in ['csv', 'xlsx', 'xls']:  # Validating the data
                        try : 
                        # Save the uploaded file to the model (instance)
                            instance = UploadedFile.objects.create(file=file)  # Store the file in model
                            file_path = instance.file.path

                            # Read and process this file with pandas
                            if file_extension == 'csv':
                                data = pd.read_csv(file_path)
                            else:
                                data = pd.read_excel(file_path)

                            # Clean the data
                            
                            cleaned_data = clean_data(data)

                            # Perform data analysis
                            analysis = perform_data_analysis(data)

                            # Generate visualizations
                            visualizations = generate_visualizations(cleaned_data)

                            # Render the results
                            return render(request, 'uploads.html', context={
                                'message': 'File uploaded and analyzed!',
                                'analysis': analysis,
                                'visualizations': visualizations,
                                'MEDIA_URL': settings.MEDIA_URL,         # 
                                # 'MEDIA_URL': settings.MEDIA_URL,

                            })
                        except Exception as e :
                            log.error(f"error processing the file : {e}")

                    else:
                        log.warning("Invalid file uploaded ")
                        return render(request, 'uploads.html', {'error': 'Only CSV and Excel files are allowed.'})
            log.info("rendered the html template")
            return render(request, "uploads.html")
            
    
    except Exception as e :
        log.error(f"error occured in home during routing",{e})
def clean_data(data):  # Clean the data for analysis
    try : 
            threshold = len(data) * 0.5
            log.info("removing the columns more than 50 percent data is missing ")
            data = data.dropna(thresh=threshold, axis=1)  # Drop columns with more than 50% missing values

            # Step 2: Convert columns that should be numeric (ignoring errors) and turn non-numeric into NaN
            for col in data.select_dtypes(include=['object']).columns:
                # Try to convert strings in numeric columns into numbers; non-numeric will be turned to NaN
                data[col] = pd.to_numeric(data[col], errors='coerce')

            #TODO:FUTURE SOLUTION - NEEDED for handling non numeric col properly  
            #   
            log.info("handling the missing data and outlliers ")
            for col in data.select_dtypes(include=['number']).columns:
                missing_count = data[col].isnull().sum()

                if missing_count > 0:
                    try : 
                    # Check if the column has outliers using IQR
                        Q1 = data[col].quantile(0.25)
                        Q3 = data[col].quantile(0.75)
                        IQR = Q3 - Q1
                        lower_bound = Q1 - 1.5 * IQR
                        upper_bound = Q3 + 1.5 * IQR

                        # Handle missing values: Use median if skewed, else use mean
                        skewness = data[col].skew()
                        if abs(skewness) > 1:
                            data[col] = data[col].fillna(data[col].median())
                        else:
                            data[col] = data[col].fillna(data[col].mean())

                        # Handle outliers (capping)
                        data[col] = np.clip(data[col], lower_bound, upper_bound)
                    except Exception as e :
                        log.error(f"error during data preprocessing , {e}")    

            # Remove duplicates
            log.info("removed duplicates")
            data = data.drop_duplicates()

            log.info("Data cleaning Completed!")
            return data
    except Exception as e :
        log.error(f"some error occured during cleaning , {e}")

def perform_data_analysis(data):  # Perform analysis on the cleaned data
    try : 

        analysis = {}
        analysis['head'] = data.head(5).to_html()  # First few rowss

        descriptive = data.describe().T
        summarise = pd.DataFrame({
            'Countd': data.shape[0],
            'Null': data.isnull().sum(),
            'Null%': data.isnull().mean() * 100,
            'Cardinality': data.nunique()
        })
        analysis['descriptive'] = descriptive.to_html(classes ='table table-striped')
        analysis['summarise'] = summarise.to_html(classes='table table-striped')
        analysis['full_table'] = data.to_html(classes='table table-striped')
        log.info("Data Analysis Completed!")
        return analysis
    except Exception as e : 
        log.error(f"error occured during data analysis process" ,{e} )




def generate_visualizations(data):
   

    plots = {}
    try:
        output_dir = os.path.join(settings.MEDIA_ROOT, 'plots')
        os.makedirs(output_dir, exist_ok=True)

        for col in data.select_dtypes(include=['float64', 'int64']):
            try:
                fig, ax = plt.subplots(figsize=(20, 10))
                sns.histplot(data[col], kde=True, ax=ax, color='skyblue')
                ax.set_title(f"Histogram of {col}", fontsize=18)
                ax.set_xlabel(f"{col} Values", fontsize=16)
                ax.set_ylabel("Frequency", fontsize=16)
                ax.tick_params(axis='both', which='major', labelsize=14)
                ax.grid(True, linestyle='--', alpha=0.7)
                plot_path = os.path.join(output_dir, f"{col}_histogram.png")
                plt.savefig(plot_path)
                plt.close(fig)
                plots[f"{col}_histogram"] = os.path.relpath(plot_path, start=settings.MEDIA_ROOT)
            except Exception as e:
                log.warning(f"Failed to generate histogram for {col}: {str(e)}")

        corr = data.corr()
        highly_corr = corr[(corr.abs() > 0.7) & (corr != 1.0)].stack().reset_index()
        for _, (col1, col2, value) in highly_corr.iterrows():
            try:
                fig, ax = plt.subplots(figsize=(20, 10))
                sns.scatterplot(x=data[col1], y=data[col2], ax=ax, color='green')
                ax.set_title(f"Scatter plot: {col1} vs {col2}", fontsize=18)
                ax.set_xlabel(f"{col1} Values", fontsize=16)
                ax.set_ylabel(f"{col2} Values", fontsize=16)
                ax.tick_params(axis='both', which='major', labelsize=14)
                ax.grid(True, linestyle='--', alpha=0.7)
                plot_path = os.path.join(output_dir, f"{col1}_vs_{col2}_scatter.png")
                plt.savefig(plot_path)
                plt.close(fig)
                plots[f"{col1}_vs_{col2}_scatter"] = os.path.relpath(plot_path, start=settings.MEDIA_ROOT)
            except Exception as e:
                log.warning(f"Failed to generate scatter plot for {col1} vs {col2}: {str(e)}")

        log.info("Visualization generation completed.")
        return plots
    except Exception as e:
        log.error(f"Error during visualization generation: {str(e)}")
        raise


    

