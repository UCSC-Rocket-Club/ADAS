#include <stdio.h>
#include <string.h>
#include <conio.h>


int main (void) 
{
	int i = 0;
	int size = 20;
	char Str[size];
	char* password = "feed me\n";

	while (1)
	{
		//fgets(Str, size, stdin);
		// printf("%s", Str);

		//if (strcmp(Str, password) == 0)
		if(kbhit())
		{
			printf("%d\n", i);
			fflush(stdout);
		}

		i++;
		Str[0] = '\0';
	}

	return 0;

}