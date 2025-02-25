import sys
sys.path.append("../")

def save_processed_integrated_data_meta(db_client, mongo_client, meta_info):
    
    ms_name = meta_info['ms_name']
    bucket_name = meta_info['bucket_name']
    ingestion_type = meta_info['ingestion_type']
    ingestion_param = meta_info['ingestion_param']
    integration_param = meta_info['integration_param']
    processing_type = meta_info['processing_type']
    process_param = meta_info['process_param']
    
    
    ##########################################          
    # 1. Data Manipulation: dataset ingestion---> data preprocessing ---> data integration 
    data = ingestion_processing_integration(db_client, ingestion_type, ingestion_param, processing_type, process_param, integration_param)
    # 2. Save Data##########################
    db_client.write_db(bucket_name, ms_name, data)
    # 3. Save Meta##########################
    meta_info['integration_param']['integration_frequency'] = meta_info['integration_param']['integration_frequency'].total_seconds()
    mongo_client.insert_document(bucket_name, ms_name, meta_info)
    
    
    
def ingestion_processing_integration(db_client, ingestion_type, ingestion_param, processing_type, process_param, integration_param):
    
    from Clust.clust.data import data_interface
    multiple_dataset = data_interface.get_data_result(ingestion_type, db_client, ingestion_param)

    # 2. Data Preprocessing
    if process_param is None:
        pass
    else:
        from Clust.clust.preprocessing import processing_interface
        multiple_dataset = processing_interface.get_data_result(processing_type, multiple_dataset, process_param)

    # 3. Data Integration
    from Clust.clust.integration import integration_interface
    data = integration_interface.get_data_result('multiple_dataset_integration', multiple_dataset, integration_param)

    
        
    return data


def get_process_param_by_level(level):
    """
    Args:
        level (int): cleaning level
    Returns:
        process_param(dict): process_param 
    """
    refine_param = {"remove_duplication": {"flag": False},"static_frequency": {"flag": False, "frequency": None}}
    certain_param = {'flag': False}
    uncertain_param = {'flag': False}
    imputation_param = {"flag": False}
    
    if level == 0:
        pass 
    if level >= 1:
        refine_param = {"remove_duplication": {"flag": True},"static_frequency": {"flag": True, "frequency": None}}
        
    if level >= 2:
        certain_param['flag'] = True
        
    if level >= 3:
        imputation_param = {
            "flag": True,
            "imputation_method": [{"min": 0, "max": 2, "method": "linear", "parameter": {}}],
            "total_non_NaN_ratio": 90
        }
        
    if level >= 4:
        uncertain_param = {'flag': True, "param": {
            "outlierDetectorConfig": [{'algorithm': 'IQR', 'percentile': 99,'alg_parameter': {'weight': 100}}]}}

    process_param = {'refine_param': refine_param,
                     'outlier_param': {"certain_error_to_NaN":  certain_param, "uncertain_error_to_NaN": uncertain_param}, 
                     'imputation_param': imputation_param}

    return process_param


    