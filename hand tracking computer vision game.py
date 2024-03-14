import pandas as pd

# Read text data
with open(r"C:\Users\Asus\Desktop\agricultural model training data set.txt",) as file:
    text_data = file.read().splitlines()

# Convert to dataframe
df = pd.DataFrame(text_data, columns=['Column Name'])

# Save dataframe to CSV
df.to_csv('output.csv', index=False)



