mkdir -p submission && while IFS= read -r file; do cp "$file" submission/; done < files_to_submit.txt