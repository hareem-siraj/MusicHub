# import pandas as pd

# # Load the CSV file into a DataFrame
# file_path = 'cleaned_new.csv'
# df = pd.read_csv(file_path)

# # Create an empty DataFrame to store new rows
# new_df = pd.DataFrame(columns=df.columns)

# # Check the type of new_df
# print(type(new_df))  # Add this line to check the type

# # Iterate through each row in the DataFrame
# for index, row in df.iterrows():
#     # Check if there are multiple artists for the song
#     artists = row['Artist_Name'].split('&')
#     if len(artists) > 1:
#         # Duplicate the row for each additional artist
#         for artist in artists[1:]:
#             new_row = row.copy()  # Copy the original row
#             new_row['Artist_Name'] = artist  # Replace the artist name
#             new_df = new_df.append(new_row, ignore_index=True)  # Append the new row to the new DataFrame
#     else:
#         new_df = new_df.append(row, ignore_index=True)  # Append the original row if there's only one artist

# # Save the updated DataFrame to a new CSV file
# output_file_path = 'final.csv'
# new_df.to_csv(output_file_path, index=False)

# print("CSV file has been updated with separate entries for multiple artists.")


import pandas as pd

# # Assuming your data is stored in a CSV file named 'tracks.csv'
# data = pd.read_csv('new.csv')

# # Remove rows with null values in the 'Artist_ID' column
# cleaned_data = data.dropna(subset=['Artist_ID'])
# cleaned_data = data.dropna(subset=['Track_ID'])
# cleaned_data = data.dropna(subset=['Album_ID'])
# cleaned_data = data.dropna(subset=['Genre'])
# cleaned_data['Genre'].fillna(cleaned_data.mode().iloc[0])
# cleaned_data = data.drop_duplicates()

# # Now 'cleaned_data' contains rows without null values in the 'Artist_ID' column
# # Define the file path for the new CSV file
# output_file_path = 'final.csv'

# # Save the cleaned data to a new CSV file
# cleaned_data.to_csv(output_file_path, index=False)

# print("Cleaned data has been saved to:", output_file_path)

data = pd.read_csv('final.csv')
#fill duplicates in Genre column
data['Genre'].fillna(data['Genre'].mode()[0], inplace=True)
#add data in csv
data.to_csv('last.csv', index=False)
print("Cleaned data has been saved to:", 'last.csv')

