# rename files with space in them.

for file in *" "*.csv; do
    if [[ -f "$file" ]]; then
        new_name="${file// /-}"
        mv "$file" "$new_name"
        echo "Renamed: '$file' -> '$new_name'"
    fi
done
