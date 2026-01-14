build_dir="rpmbuild/RPMS/noarch"
# Liste des noms de packages séparés par des espaces : Tous les packages doivent être livrés sur un même serveur et éventuellement dans des repos différents
pkg_names="iv-patch-records"
USAGE="Usage : deliver.sh [PKG_FILE_NAME]
	PKG_FILE_NAME : Nom du fichier RPM à délivrer
	Ce script ira chercher la dernière version des packages  $pkg_names dans le répertoire de build : $build_dir (sauf sous el5)
	Le répertoire de build et les packages sont configurés directement au début de ce script.

	Pour suivre la règle \"Aucune configuration de topologie interne dans github\",	
	le serveur de destination pour la livraison est configuré dans le fichier ~/deliver.conf au format : 

	DELIVERY delivery-hostname package-1;package-2;

	Note d'utilisation de script sous el5 : 
		Sous el5 ce script ne peut pas determiner quel est le dernier fichier de package car 
	\"sort --version-sort\" n'existe pas. Comme je n'ai pas envie de l'écrire en bash, 
	j'ai ajouté un paramètre optionnel pour préciser le fichier du package.
"

if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
    echo -e "$USAGE" 
    exit 2
fi

repos_to_sync=""

# Le fichier deliver.conf, stocké dans le répertoire de l'utilisateur contient une ligne taguée DELIVERY avec par exemple:
# DELIVERY vs-ics-prd-sas-fr-502 iv-vocal-server;iv-vocal-server-applib;pnum;
# Cette ligne indique sur quel serveur doivent être délivrés quels packages
delivery_server=$(grep "DELIVERY.*${pkg_name};" ~/deliver.conf | awk '{print $2}')
if [[ "$delivery_server" == "" ]]; then
	echo "Pas de serveur trouvé pour la livraison du package ${pkg_name}"
	echo "Voici le contenu de ~/deliver.conf :"
	cat ~/deliver.conf
	exit 1
fi

for pkg_name in ${pkg_names}; do

	# A partir de la liste des rpm présents dans le répertoire de build on trouve le rpm avec le numéro de version le plus élevé
	# awk retire les noms de paquets contenant le nom du paquet choisi
	# sed supprime le chemin avant le nom du fichier
	# sort possède un magnifique paramètre pour trier suivant la version
	# on prend le dernier de la liste qui est dans l'ordre croissant
	if [[ "$1" == "" ]]; then
		if [[ "$(sort --version | grep 8)" == "" ]]; then
			echo -e "Je ne peux pas trouver la dernière version tout seul, voici les packages dans $build_dir :" 
			for r in `ls -1 $build_dir/*.rpm`; do
				basename $r;
			done
			exit 3
		fi
		last_rpm_file=$(ls -1 ${build_dir}/${pkg_name}*.rpm | awk '/'${pkg_name}'-[0-9]/ {print $0}' | sed 's#.*/##'| sort --version-sort | tail -n 1) 
	else
		last_rpm_file=$1
	fi


	# pour retrouver l'architecture à partir du nom de package 
	# Dans cette partie variable le caractère - marque le début de la partie contenant le n° de package et l'achitecture, on l'extrait avec le premier awk
	# Ensuite on utilise le . comme séparateur et le deuxième champ contiendra notre architecture, i.e : el5, el6, el7, el... ou noarch
	# A noter que cpack utilise un '.' pour séparer le nom de package de sa version alors que rpm-build utilise '-'
	rpm_architecture=$(echo $last_rpm_file | awk -F - '{print $NF}' | awk -F . '{print $2}')

	echo $last_rpm_file
	echo $rpm_architecture

	# Il reste à livrer le package avec un bête scp. (L'utilisateur aura copié sa clé ssh avec un ssh-copy-id delivery@[delivery_server]
	# (Au préalable on crée le répertoire de destination s'il n'existe pas)
	ssh delivery@$delivery_server "mkdir -p $rpm_architecture"
	scp ${build_dir}/$last_rpm_file delivery@$delivery_server:$rpm_architecture


	# Le package est ensuite copié puis signé dans un channel 
	delivery_channel=$(grep "CHANNEL.*${pkg_name};" ~/deliver.conf | awk '{print $2}')
	if [[ "$delivery_channel" == "" ]]; then
		echo "Pas de channel trouvé pour la mise à disposition du package ${pkg_name}"
		echo "Voici le contenu de ~/deliver.conf :"
		cat ~/deliver.conf
		exit 1
	fi
	channel_dir=/var/www/html/pub/distro/$delivery_channel
	ssh delivery@$delivery_server "sudo cp $rpm_architecture/$last_rpm_file $channel_dir"
	ssh delivery@$delivery_server "sudo rpm --addsign $channel_dir/$last_rpm_file"
	ssh delivery@$delivery_server "sudo createrepo $channel_dir"

	if [[ "$(echo $repos_to_sync | grep $delivery_channel)" == "" ]]; then
		repos_to_sync="$delivery_channel $repos_to_sync"
	fi

done

#
# On synchronise les dépôts modifiés à la fin
#
for repo in $repos_to_sync; do
	ssh delivery@$delivery_server "sudo /usr/bin/spacewalk-repo-sync --channel $delivery_channel"
done
