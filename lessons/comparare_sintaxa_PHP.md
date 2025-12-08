# 🔄 Comparare sintaxa PHP foreach



# ✔️ 1. Varianta cu sintaxa alternativă foreach : ... endforeach
## <?php foreach($books as $key_book => $book) : ?>
##     <h1>Titlul cărții: <?php echo $book['title']; ?></h1>
##     <h2>Autorul cărții: <?php echo $book['author']; ?></h2>
## <?php endforeach; ?>

Observații:

## Corect este $book['author'], nu $book['title'] pentru autor (ai scris de două ori titlul).

Sintaxa aceasta este foarte utilă în fișiere care conțin mult HTML.

E mai curată, mai lizibilă, mai ușor de întreținut.

# ✔️ 2. Varianta cu concatenare în interiorul blocului foreach { ... }
### foreach ($books as $book) {
###    echo "<h1>$book[title]</h1>"
###       . "<h2>$book[author]</h2>"
###       . "<br>";
### }

## Observații:

Funcționează, dar:

Nu este recomandat să scrii $book[title] fără ghilimele, deoarece PHP încearcă să caute o constantă title.

Forma corectă este:

### foreach ($books as $book) {
###     echo "<h1>{$book['title']}</h1>"
###        . "<h2>{$book['author']}</h2>"
###        . "<br>";
### }

# 🔍 Diferențele principale
## Caracteristică	Sintaxa alternativă foreach: endforeach	Sintaxa clasica foreach { }
## Citibilitate	✔ foarte bună pentru HTML	❌ mai greu de citit în HTML
## Siguranță / stil	Variabilele sunt printate clar	Necesită atenție la ghilimele și concatenare
## Recomandat pentru	Template-uri, view-uri, output HTML	Output rapid sau logică în PHP pur
## Risc de erori	Mic	Mai mare dacă omiți ghilimelele
# 🎯 Concluzie

## ✔ Ambele variante funcționează.
## ✔ Prima este recomandată când ai mult HTML.
## ✔ A doua este ok, dar necesită ghilimele și concatenare corectă.