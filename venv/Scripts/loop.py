
secret_number = 'hammed'
guess = ' '
guess_limit = 0
while guess != secret_number and guess_limit != 3:
    guess = input('enter a number ')
    if guess == secret_number:
        print('you win')
    guess_limit += 1

print('you lose')




