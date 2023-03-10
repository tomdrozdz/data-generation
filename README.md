* Na razie cechy `PersonNumber` w `Household` i `Schedule` w `Person` są zdefiniowane
  osobno, bo ułatwia to trochę kod w `Builder`, chyba nie będzie sytuacji gdzie jedna
  z tych cech nie będzie występować.
* To pole `user_defined_extras` raczej można wrzucić do `features`, jeszcze nie wiem
  czy taki podział się do czegoś przyda, ogólnie ma to reprezentować coś, co łatwo
  można dorzucić do jednego z obiektów bez modyfikacji reszty
* Jeszcze można by usunąć to pole klas `BASIC_FEATURES` i podawać cechy jakie chcemy
  mieć prosto do buildera, co w sumie ułatwiłoby dodawanie tych "extra" cech, ale nie
  mamy wtedy jakiejś zdefiniowanej bazy, którą obsługiwałyby defaultowe generatory z
  biblioteki.

Łatwe QoL zmiany:
* dict `requirements` i `REQUIRES` w `Generator` można zamienić na definiowanie wymagań
  od razu w `.generate(...)` i inspectowanie sygnatury
* dorobić możliwość zwracania np. `tuple[Age, Sex]` z `Generator`, żeby jeden generator
  mógł ogarniać kilka cech
