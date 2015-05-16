print ('Welcome to Bestrip! The best trip search engine in the world!' + '\n')
print ('Please, answer these questions to find your trip!' + '\n')

city = raw_input ('Where do you want to go?' + '\n')
departureDate = raw_input ('When do you want to go?' + '\n' + '(Format : dd/mm/yyyy)')
returnDate = raw_input ('When do you want to return?' + '\n' + '(Format : dd/mm/yyyy)')
maxPrice = raw_input('Which is the maximum price that a trip must have?')
numberOfStars = raw_input ('How many stars the hotel must have ?' + '\n')

activities = raw_input ('Tell us about the kind of activities you like!' + '\n' + ' (Format:separate using commas for each preference)' + '\n')
transport = raw_input ('Would you like to use public transport during your trip?' + '\n')

print ('Thank you very much, finding the best trip according to your preferences ... ' + '\n')
