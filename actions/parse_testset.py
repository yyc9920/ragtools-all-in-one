import csv

def removeInvalidGroundTruths(testset):
    """
    This function removes items from the testset where the ground truth is not valid.

    Parameters:
    testset (list): A list of dictionaries, where each dictionary represents a test item.
                    Each dictionary should have a 'ground_truth' key.

    Returns:
    list: A new list of dictionaries, where invalid ground truths have been removed.
    """
    new_testset = []
    for item in testset:
        if item['ground_truth'] != "The answer to given question is not present in context":
            new_testset.append(item)

    return new_testset


def modifyMetadata(testset, base_path):
    """
    This function modifies the 'metadata' field in each item of the testset.

    Parameters:
    testset (list): A list of dictionaries, where each dictionary represents a test item.
                    Each dictionary should have a 'metadata' key, which is a list containing a dictionary.

    base_path (str): The base path to be removed from the metadata.

    Returns:
    list: The modified testset with updated 'metadata' fields.
    """
    for item in testset:
        if 'metadata' in item:
            item['metadata'] = ' | '.join(
                (key + ' : ' + value) for key, value in item['metadata'][0].items())
            item['metadata'] = item['metadata'].replace(',', ' |')
            item['metadata'] = item['metadata'].replace(base_path, '')
            item['metadata'] = item['metadata'].replace('\\', '/')

    return testset


def saveDictToCsv(dict_data, filename):
    """
    This function saves a list of dictionaries to a CSV file.

    Parameters:
    dict_data (list): A list of dictionaries, where each dictionary represents a row in the CSV file.
                      The keys of the dictionaries are used as column headers.

    filename (str): The name of the CSV file to be created.

    Returns:
    None
    """
    fieldnames = dict_data[0].keys()
    with open(filename, mode='w', newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for item in dict_data:
            writer.writerow(item)


