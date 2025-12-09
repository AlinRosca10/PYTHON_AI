# 🔗 Trilema Interoperabilității



Scalabilitate, Modularitate și Securitate — trei dimensiuni care se influențează reciproc.

Fiecare lecție aici este scurtă și la obiect, cu exemple practice.


### Trei piloni ai cursului: 

- 📈 **Scalabilitate**: cum reacționează sistemul când crește numărul de utilizatori.
- 🧩 **Modularitate**: cum împarți sistemul în părți ușor de înțeles.
- 🔒 **Securitate**: cum protejezi datele și disponibilitatea.


## 📈 Scalabilitate — Performanță, Disponibilitate, Consistență

### Componentele trilemei scalabilității: 

- ⚡ **Performanță**: latență și throughput.
- ☁️ **Disponibilitate**: uptime și recuperare.
- 🔁 **Consistență**: versiuni ale datelor în sisteme distribuite.

### 💡 Exercițiu practic:

Gândește un microserviciu care trebuie să rămână disponibil când sunt 10k utilizatori în același timp. Ce trade-off faci?

## 🧩 Modularitate — Coeziune, Cuplare, Extensibilitate

### Componentele trilemei modularității: 

- 🔗 **Coeziune internă**: funcționalitățile unui modul se potrivesc între ele.  
- 🤝 **Cuplare redusă**: module independente, ușor de schimbat.  
- ➕ **Extensibilitate**: adăugarea de funcționalități fără să „strici” ce există.

### 💡 Exercițiu practic: 

Proiectează un modul de Autentificare pentru o aplicație web.

## 🔒 Securitate — Confidențialitate, Integritate, Disponibilitate

### Componentele trilemei securității:

- 🔐 **Confidențialitate**: prevenirea accesului neautorizat
- 🛡️ **Integritate**: protejarea datelor împotriva modificărilor neautorizate
- 🕒 **Disponibilitate**: asigurarea accesului legitim la resurse

### 💡 Exercițiu practic: 

Proiectează un serviciu de e-mail. Maximizați Confidențialitatea și Integritatea la cel mai înalt nivel. Decideți să criptați fiecare email individual cu chei unice și complexe, iar fiecare acces necesită o revalidare biometrică.
Compromisul: Disponibilitatea va suferi. Procesul de criptare/decriptare și autentificare constantă va încetini drastic serverele de email, făcând serviciul lent și greu de utilizat. Trebuie găsit un echilibru optim între cele trei obiective.



