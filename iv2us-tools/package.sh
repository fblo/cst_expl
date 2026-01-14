# Le n° de commit est extrait avec la commande git
git_hash=$(git log -1 --pretty=format:%h)

# Le n° de version est directement ici 
version="1.0"

tag_version=$(git describe --tags | awk -F "-" '/^v[0-9.]+(-[0-9]+)?$/ { print substr($1,2)}')
tag_package=$(git describe --tags | awk -F "-" '/^v[0-9.]+(-[0-9]+)?$/ { print $2}')
if [[ "$tag_version" == "" || "$tag_package" == "" ]]; then
	echo "ERREUR : Le commit courant : $git_hash n'a pas de tag de version-package de la forme : v...-.."
	exit 1
fi

if [[ "$tag_version" != "$version" ]]; then
	echo "ERREUR : Le fichier package.json ne contient pas la même version que le tag ($version dans le json, $tag_version dans le tag)"
	exit 2
fi

mkdir -p generated
echo $version-$tag_package-$git_hash > generated/version

# Injecte le n° de version dans le fichier spec de construction du package rpm. (Toute la ligne commençant par Version est remplacée)
sed '/^Version:/s/.*/Version:        '$tag_version'/g' packaging/iv-patch-records.template | sed '/^Release:/s/.*/Release:        '$tag_package'/g' > generated/iv-patch-records.spec

rpmbuild -bb generated/iv-patch-records.spec --define "_topdir `pwd`/rpmbuild"
