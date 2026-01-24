#!/bin/bash
# Script pour tester et comparer les tailles des images optimisées

set -e

echo "🐳 Test des Containerfiles optimisés pour CCCP Dashboard"
echo "========================================================"

# Fonction pour construire et mesurer une image
build_and_measure() {
    local name=$1
    local dockerfile=$2
    
    echo ""
    echo "🏗️  Construction de $name..."
    echo "   Dockerfile: $dockerfile"
    
    # Construction
    if podman build -f "$dockerfile" -t "cccp_$name" .; then
        # Mesure de la taille
        size=$(podman images "cccp_$name" --format "{{.Size}}")
        echo "   ✅ Build réussi"
        echo "   📏 Taille: $size"
        
        # Test rapide
        echo "   🧪 Test de démarrage..."
        if timeout 10s podman run --rm "cccp_$name" python3 -c "import flask; print('Flask OK')" 2>/dev/null; then
            echo "   ✅ Test de démarrage réussi"
        else
            echo "   ⚠️  Test de démarrage échoué (peut être normal)"
        fi
    else
        echo "   ❌ Build échoué"
    fi
}

echo "📋 Containerfiles disponibles :"
ls -la Containerfile.*

# Construire chaque version
build_and_measure "original" "Containerfile.test"
build_and_measure "optimized" "Containerfile.optimized" 
build_and_measure "minimal" "Containerfile.minimal"
build_and_measure "alpine" "Containerfile.alpine"
build_and_measure "distroless" "Containerfile.distroless"

echo ""
echo "📊 Résumé des tailles :"
podman images | grep cccp_ | head -10

echo ""
echo "💡 Recommandations :"
echo "   - Containerfile.minimal : Meilleur équilibre taille/compatibilité"
echo "   - Containerfile.alpine : Plus petit si compatible glibc/musl"
echo "   - Containerfile.distroless : Plus sécurisé mais complexe"
echo "   - Containerfile.optimized : Meilleure maintenabilité"

echo ""
echo "🚀 Pour utiliser l'image optimisée :"
echo "   podman tag cccp_minimal cccp_dashboard:latest"
echo "   podman run -p 5000:5000 cccp_dashboard:latest"