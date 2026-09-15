BEGIN { FS = "," }
NR > 1 {
  field = $2
  sub(/\r$/, "", field)
  if (field ~ /^".*"$/) {
    sub(/^"/, "", field)
    sub(/"$/, "", field)
    gsub(/""/, "\"", field)
  }
  if (field == name) {
    print $1
    exit
  }
}
