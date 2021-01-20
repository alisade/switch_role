#......
for i in $(~/environment/yaml2array.py); do
  alias $i="source <(~/environment/switch_role.py $i)"
done
__k8s_cluster() {
  [ -n "$KUBECONFIG" ] && printf -- " $(basename $KUBECONFIG)"
}
PS1='\[\033[01;32m\]$(_cloud9_prompt_user)\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]$(__git_ps1 " (%s)" 2>/dev/null)\[\033[01;33m\]$(__k8s_cluster)\[\033[00m\] $ '