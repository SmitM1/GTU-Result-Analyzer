import numpy as np
import pandas as pd

def process_csv(filepath, branch_code):
    """
    Process subject columns in the DataFrame by splitting subject names and grades,
    creating new columns for subjects and grades, and rearranging columns.

    Parameters:
        df (DataFrame): Input DataFrame containing subject names and grades.

    Returns:
        DataFrame: Processed DataFrame with subject names and grades extracted.
    """

    df = pd.read_csv(filepath)
    
    # Selecting columns related to subjects and results
    df2 = df[['St_Id', 'name', 'BR_CODE', 
              'SUB1NA', 'SUB2NA', 'SUB3NA', 'SUB4NA', 'SUB5NA', 'SUB6NA', 'SUB7NA', 'SUB8NA', 'SUB9NA', 'SUB10NA', 
              'SUB11NA', 'SUB12NA', 'SUB13NA', 'SUB14NA', 'SUB15NA', 
              'SUB1GR', 'SUB2GR', 'SUB3GR', 'SUB4GR', 'SUB5GR', 'SUB6GR', 'SUB7GR', 'SUB8GR', 'SUB9GR', 'SUB10GR', 
              'SUB11GR', 'SUB12GR', 'SUB13GR', 'SUB14GR', 'SUB15GR', 
              'CURBACKL', 'SPI', 'CPI', 'CGPA', 'TOTBACKL']]

    result_df = pd.DataFrame()
    
    # Iterate over each row in the DataFrame
    for index, row in df2.iterrows():
        # Iterate over the subject columns
        for i in range(1, 16):
            sub_na_col = 'SUB{}NA'.format(i)
            sub_gr_col = 'SUB{}GR'.format(i)

            # Check if the subject name and grade columns are not NaN
            if pd.notna(row[sub_na_col]) and pd.notna(row[sub_gr_col]):
                # Split the subject names and grades
                subjects = row[sub_na_col].split(', ')
                grades = row[sub_gr_col].split(', ')

                # Iterate over each subject and grade
                for j, subject in enumerate(subjects):
                    grade = grades[j].strip() if j < len(grades) else None

                    # Create new columns for subjects and grades
                    result_df.at[index, subject] = grade

    # Concatenate the original DataFrame with the result DataFrame
    df3 = pd.concat([df2, result_df], axis=1)

    # Drop the original subject name and grade columns
    df3.drop(columns=[f'SUB{i}NA' for i in range(1, 16)] + [f'SUB{i}GR' for i in range(1, 16)], inplace=True)

    # Rearrange the columns to place specified columns at the end
    specified_columns = ['CURBACKL', 'SPI', 'CPI', 'CGPA', 'TOTBACKL']
    remaining_columns = [col for col in df3.columns if col not in specified_columns]

    df3 = df3[remaining_columns + specified_columns]
    
    #removing the columns of subjects which contain all NaN values
    df3 = df3.dropna(axis=1, how='all')

    df3['St_Id'] = df3['St_Id'].str.split('_').str[1]

    df3.rename(columns={'St_Id' : 'ENROLLMENT NO.', 'name' : 'NAME OF STUDENT', 'CURBACKL' : 'No. of Backlogs', 'TOTBACKL' : 'TOTAL BACKLOG'}, inplace=True)

    df3 = df3.sort_values(by='ENROLLMENT NO.')
    
    df4 = df3.copy()
    input_branch = int(branch_code)
    df5 = df4[df4['BR_CODE'] == input_branch]
    
    #removing the columns of subjects which contain all NaN values
    df5 = df5.dropna(axis=1, how='all')

   

    # df5.set_index('SR NO', inplace=True)
    
    def count_fail(count_back):
        count = 0
        
        for values in df5['No. of Backlogs']:
            if values==count_back:
                count+=1
        return count

    dict_2 = {'No of student fail in 6 subject': count_fail(6), 'No of student fail in 5 subject': count_fail(5), 'No of student fail in 4 subject': count_fail(4), 'No of student fail in 3 subject': count_fail(3), 'No of student fail in 2 subject': count_fail(2), 'No of student fail in 1 subject': count_fail(1), 'No of student pass in all subject': count_fail(0)}
    total_sum = sum(value for value in dict_2.values())

    dict_2['Total'] = total_sum
    dict_2['Total result in %'] = np.round((dict_2['No of student pass in all subject']/total_sum) *100, decimals=2)

    df_3 = pd.DataFrame(columns=df5.columns[3:-5])

    def count_student_grades(df_5, df_3):
        # Initialize a dictionary to store grade counts for each subject
        grade_counts = {subject: df_5[subject].value_counts() for subject in df_3.columns}
        
        # Initialize an empty DataFrame to store grade counts
        grade_counts_df = pd.DataFrame(grade_counts).fillna(0).astype(int)
        
        # Set index names to grade names
        grade_counts_df.index.name = 'Grade'
        
        # Add this dataframe to df_3
        df_3 = pd.concat([grade_counts_df, df_3], axis=0)
        
        # Reset index
        df_3.reset_index(drop=True, inplace=True)
        
        # Set 'Subject name' as a new column
        df_3['Subject name'] = [
            'No of student in AA', 
            'No of student in AB', 
            'No of student in BB', 
            'No of student in BC', 
            'No of student in CC', 
            'No of student in CD', 
            'No of student in DD', 
            'No of student in FF',
        ]
        
        # Set 'Subject name' as index
        df_3.set_index('Subject name', inplace=True)
        
        # Calculate the total sum of each column
        total_sum = df_3.sum(axis=0)
        
        # Add the total sum as the last row
        df_3.loc['Total'] = total_sum

        df_4 = df_3.copy()
        
        df_4 = (df_4 / total_sum[0]) * 100
        
        diff_ff_total = df_4.loc['Total'] - df_4.loc['No of student in FF']

        df_4.loc['PER SUBJECT RESULT'] = diff_ff_total

        df_4 = df_4.applymap(lambda x: f"{x:.2f}%")
        
        # Drop unwanted index columns
        df_3.columns.name = None

        return df_3, df_4

    df2_3, df_4 = count_student_grades(df5, df_3)
    
    sr_no2 = np.arange(1, df5.shape[0] + 1)
    df5.index = sr_no2
    df5.index.name = 'SR NO'
    # df5.set_index('SR NO', inplace=True)

    def export_to_csv(df5, dict_2, df2_3, df_4):
        # Export df5 to CSV with a blank line after
        with open('combined_data.csv', 'w') as f:
            df5.to_csv(f, index=True)
            f.write('\n\n')

        # Export dict_2 to CSV with a blank line after
        with open('combined_data.csv', 'a') as f:
            pd.DataFrame.from_dict(dict_2, orient='index').to_csv(f, header=False, index=True)
            f.write('\n\n')

        # Export df2_3 to CSV with a blank line after
        with open('combined_data.csv', 'a') as f:
            df2_3.to_csv(f, index=True)
            f.write('\n\n')

        # Export df_4 to CSV with a blank line after
        with open('combined_data.csv', 'a') as f:
            df_4.to_csv(f, index=True)
            f.write('\n\n')

    export_to_csv(df5, dict_2, df2_3, df_4)