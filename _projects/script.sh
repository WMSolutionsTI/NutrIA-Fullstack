#!/bin/bash

# =============================================================================
# GitHub Project Manager Script
# =============================================================================
# Script para criar e gerenciar projetos GitHub via terminal usando gh CLI
# Autor: Engenheiro de Software
# Data: 2026-03-07
# Versão: 2.2
#
# Requisitos:
# - GitHub CLI (gh) instalado e configurado
# - yq instalado para parsing YAML
# - Permissões adequadas no repositório
# =============================================================================

set -euo pipefail

# Cores para output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Variáveis globais
YAML_FILE="fase-07-funcionalidades-negocio.yaml"
OWNER="WMSolutionsTI"
REPO="NutriSaas"
PROJECT_NAME="fase-07-funcionalidades-negocio"
PROJECT_ID=""
PROJECT_NUMBER=""

# =============================================================================
# FUNÇÕES DE UTILIDADE
# =============================================================================

# Função para logging com cores
log() {
    local level="$1"
    local message="$2"

    case "$level" in
        "INFO")  echo -e "${BLUE}[INFO]${NC} $message" ;;
        "SUCCESS") echo -e "${GREEN}[SUCCESS]${NC} $message" ;;
        "WARNING") echo -e "${YELLOW}[WARNING]${NC} $message" ;;
        "ERROR") echo -e "${RED}[ERROR]${NC} $message" ;;
    esac
}

# Validar se dependências estão instaladas
check_dependencies() {
    log "INFO" "Verificando dependências..."

    if ! command -v gh &> /dev/null; then
        log "ERROR" "GitHub CLI (gh) não encontrado. Instale: https://cli.github.com/"
        exit 1
    fi

    if ! command -v yq &> /dev/null; then
        log "ERROR" "yq não encontrado. Instale: https://github.com/mikefarah/yq"
        exit 1
    fi

    if ! command -v jq &> /dev/null; then
        log "ERROR" "jq não encontrado. Instale: apt install jq / brew install jq"
        exit 1
    fi

    # Verificar se está autenticado no GitHub
    if ! gh auth status &> /dev/null; then
        log "ERROR" "Não autenticado no GitHub. Execute: gh auth login"
        exit 1
    fi

    log "SUCCESS" "Todas as dependências verificadas"
}

# Validar arquivo YAML
validate_yaml() {
    local yaml_file="$1"

    if [[ ! -f "$yaml_file" ]]; then
        log "ERROR" "Arquivo YAML não encontrado: $yaml_file"
        exit 1
    fi

    if ! yq eval '. ' "$yaml_file" >/dev/null 2>&1; then
        log "ERROR" "Arquivo YAML inválido: $yaml_file"
        exit 1
    fi

    log "SUCCESS" "Arquivo YAML válido: $yaml_file"
}

# =============================================================================
# FUNÇÕES DE CONFIGURAÇÃO
# =============================================================================

# Ler configurações básicas do YAML
read_config() {
    log "INFO" "Lendo configurações do arquivo YAML..."

    OWNER=$(yq eval '.owner' "$YAML_FILE")
    REPO=$(yq eval '.repo' "$YAML_FILE")
    PROJECT_NAME=$(yq eval '.project.name' "$YAML_FILE")

    if [[ "$OWNER" == "null" ]] || [[ "$REPO" == "null" ]] || [[ "$PROJECT_NAME" == "null" ]]; then
        log "ERROR" "Configurações obrigatórias não encontradas (owner, repo, project.name)"
        exit 1
    fi

    log "INFO" "Owner: $OWNER"
    log "INFO" "Repo: $REPO"
    log "INFO" "Projeto: $PROJECT_NAME"
}

# =============================================================================
# FUNÇÕES DE LABELS
# =============================================================================

# Criar labels se não existirem
create_labels() {
    log "INFO" "Processando labels..."

    local labels_count
    labels_count=$(yq eval '.labels | length' "$YAML_FILE")

    if [[ "$labels_count" == "0" ]]; then
        log "INFO" "Nenhuma label definida no YAML"
        return
    fi

    for ((i=0; i<labels_count; i++)); do
        local name color description

        name=$(yq eval ".labels[$i].name" "$YAML_FILE")
        color=$(yq eval ".labels[$i].color" "$YAML_FILE")
        description=$(yq eval ".labels[$i].description" "$YAML_FILE")

        # Verificar se label já existe
        if gh label list --repo "$OWNER/$REPO" --search "$name" --json name --jq '.[].name' 2>/dev/null | grep -q "^$name$"; then
            log "INFO" "Label '$name' já existe"
        else
            # Criar nova label
            if [[ "$description" != "null" ]]; then
                if gh label create "$name" --color "${color#\#}" --description "$description" --repo "$OWNER/$REPO" >/dev/null 2>&1; then
                    log "SUCCESS" "Label '$name' criada com sucesso"
                else
                    log "ERROR" "Falha ao criar label '$name'"
                fi
            else
                if gh label create "$name" --color "${color#\#}" --repo "$OWNER/$REPO" >/dev/null 2>&1; then
                    log "SUCCESS" "Label '$name' criada com sucesso"
                else
                    log "ERROR" "Falha ao criar label '$name'"
                fi
            fi
        fi
    done
}

# =============================================================================
# FUNÇÕES DE MILESTONES
# =============================================================================

# Criar milestones se não existirem
create_milestones() {
    log "INFO" "Processando milestones..."

    local milestones_count
    milestones_count=$(yq eval '.milestones | length' "$YAML_FILE")

    if [[ "$milestones_count" == "0" ]]; then
        log "INFO" "Nenhuma milestone definida no YAML"
        return
    fi

    for ((i=0; i<milestones_count; i++)); do
        local title due_date description

        title=$(yq eval ".milestones[$i].title" "$YAML_FILE")
        due_date=$(yq eval ".milestones[$i].due_date" "$YAML_FILE")
        description=$(yq eval ".milestones[$i].description" "$YAML_FILE")

        # Verificar se milestone já existe
        if gh api "/repos/$OWNER/$REPO/milestones" --jq '.[].title' 2>/dev/null | grep -q "^$title$"; then
            log "INFO" "Milestone '$title' já existe"
        else
            # Criar nova milestone
            local milestone_data="{\"title\":\"$title\""

            if [[ "$description" != "null" ]]; then
                milestone_data="$milestone_data,\"description\":\"$description\""
            fi

            if [[ "$due_date" != "null" ]]; then
                milestone_data="$milestone_data,\"due_on\":\"${due_date}T23:59:59Z\""
            fi

            milestone_data="$milestone_data}"

            if gh api "/repos/$OWNER/$REPO/milestones" --method POST --input - <<< "$milestone_data" > /dev/null 2>&1; then
                log "SUCCESS" "Milestone '$title' criada com sucesso"
            else
                log "ERROR" "Falha ao criar milestone '$title'"
            fi
        fi
    done
}

# =============================================================================
# FUNÇÕES DE PROJETO
# =============================================================================

# Criar projeto se não existir
create_project() {
    log "INFO" "Verificando projeto..."

    # Verificar se projeto já existe
    local project_info
    project_info=$(gh project list --owner "$OWNER" --format json 2>/dev/null | jq -r --arg name "$PROJECT_NAME" '.projects[] | select(.title == $name) | "\(.id)|\(.number)"' || echo "")

    if [[ -n "$project_info" ]]; then
        PROJECT_ID=$(echo "$project_info" | cut -d'|' -f1)
        PROJECT_NUMBER=$(echo "$project_info" | cut -d'|' -f2)
        log "INFO" "Projeto '$PROJECT_NAME' já existe (ID: $PROJECT_ID, Number: $PROJECT_NUMBER)"
    else
        # Criar novo projeto
        local project_result
        project_result=$(gh project create --owner "$OWNER" --title "$PROJECT_NAME" --format json 2>/dev/null)

        if [[ -n "$project_result" ]]; then
            PROJECT_ID=$(echo "$project_result" | jq -r '.id')
            PROJECT_NUMBER=$(echo "$project_result" | jq -r '.number')
            log "SUCCESS" "Projeto '$PROJECT_NAME' criado com sucesso (ID: $PROJECT_ID, Number: $PROJECT_NUMBER)"
        else
            log "ERROR" "Falha ao criar projeto '$PROJECT_NAME'"
            exit 1
        fi
    fi
}

# Verificar se issue já está no projeto
is_issue_in_project() {
    local issue_number="$1"

    if [[ -z "$PROJECT_NUMBER" ]]; then
        return 1
    fi

    # Buscar items no projeto
    local project_items
    project_items=$(gh project item-list "$PROJECT_NUMBER" --owner "$OWNER" --format json 2>/dev/null | jq -r '.[].content.number' 2>/dev/null || echo "")

    echo "$project_items" | grep -q "^$issue_number$"
}

# Adicionar issue ao projeto
add_issue_to_project() {
    local issue_number="$1"
    local issue_url="https://github.com/$OWNER/$REPO/issues/$issue_number"

    if [[ -z "$PROJECT_NUMBER" ]]; then
        log "WARNING" "PROJECT_NUMBER não definido, não é possível adicionar ao projeto"
        return 1
    fi

    # Verificar se já está no projeto
    if is_issue_in_project "$issue_number"; then
        log "INFO" "Issue #$issue_number já está no projeto"
        return 0
    fi

    # Tentar adicionar ao projeto usando o número do projeto
    if gh project item-add "$PROJECT_NUMBER" --owner "$OWNER" --url "$issue_url" >/dev/null 2>&1; then
        log "SUCCESS" "Issue #$issue_number adicionada ao projeto"
        return 0
    else
        log "WARNING" "Falha ao adicionar issue #$issue_number ao projeto (tentativa 1)"
        # Segunda tentativa com delay
        sleep 2
        if gh project item-add "$PROJECT_NUMBER" --owner "$OWNER" --url "$issue_url" >/dev/null 2>&1; then
            log "SUCCESS" "Issue #$issue_number adicionada ao projeto (tentativa 2)"
            return 0
        else
            log "ERROR" "Falha ao adicionar issue #$issue_number ao projeto após 2 tentativas"
            return 1
        fi
    fi
}

# =============================================================================
# FUNÇÕES DE ISSUES
# =============================================================================

# Gerar checklist de tasks
generate_checklist() {
    local issue_index="$1"
    local tasks_count

    tasks_count=$(yq eval ".issues[$issue_index].tasks | length" "$YAML_FILE")

    if [[ "$tasks_count" == "0" ]]; then
        echo ""
        return
    fi

    local checklist=$'\n\n## Tasks\n'

    for ((j=0; j<tasks_count; j++)); do
        local task
        task=$(yq eval ".issues[$issue_index].tasks[$j]" "$YAML_FILE")
        checklist="$checklist"$'\n'"- [ ] $task"
    done

    echo "$checklist"
}

# Obter número da issue pelo título
get_issue_number_by_title() {
    local title="$1"
    gh issue list --repo "$OWNER/$REPO" --search "in:title \"$title\"" --json number --jq '.[0].number' 2>/dev/null || echo ""
}

# Verificar se tasks precisam ser atualizadas
need_tasks_update() {
    local issue_number="$1"
    local new_checklist="$2"

    if [[ -z "$new_checklist" ]]; then
        return 1
    fi

    local current_body
    current_body=$(gh issue view "$issue_number" --repo "$OWNER/$REPO" --json body --jq '.body' 2>/dev/null || echo "")

    # Verificar se o checklist já existe no body
    if [[ "$current_body" == *"## Tasks"* ]]; then
        # Extrair seção de tasks atual
        local current_tasks
        current_tasks=$(echo "$current_body" | sed -n '/## Tasks/,$p')

        # Comparar com novo checklist
        if [[ "$current_tasks" != "$new_checklist" ]]; then
            return 0  # Precisa atualizar
        else
            return 1  # Não precisa atualizar
        fi
    else
        return 0  # Não tem tasks, precisa adicionar
    fi
}

# Atualizar checklist de uma issue existente
update_issue_checklist() {
    local issue_number="$1"
    local new_checklist="$2"

    if [[ -z "$new_checklist" ]]; then
        return 0
    fi

    local current_body
    current_body=$(gh issue view "$issue_number" --repo "$OWNER/$REPO" --json body --jq '.body' 2>/dev/null || echo "")

    local updated_body

    # Se já tem seção de tasks, substituir
    if [[ "$current_body" == *"## Tasks"* ]]; then
        # Remover seção de tasks atual e adicionar nova
        updated_body=$(echo "$current_body" | sed '/## Tasks/,$d')
        updated_body="$updated_body$new_checklist"
    else
        # Adicionar checklist ao final
        updated_body="$current_body$new_checklist"
    fi

    if gh issue edit "$issue_number" --repo "$OWNER/$REPO" --body "$updated_body" >/dev/null 2>&1; then
        log "SUCCESS" "Checklist atualizado para issue #$issue_number"
        return 0
    else
        log "ERROR" "Falha ao atualizar checklist da issue #$issue_number"
        return 1
    fi
}

# Processar issues
process_issues() {
    log "INFO" "Processando issues..."

    local issues_count
    issues_count=$(yq eval '.issues | length' "$YAML_FILE")

    if [[ "$issues_count" == "0" ]]; then
        log "INFO" "Nenhuma issue definida no YAML"
        return
    fi

    for ((i=0; i<issues_count; i++)); do
        local title body milestone

        title=$(yq eval ".issues[$i].title" "$YAML_FILE")
        body=$(yq eval ".issues[$i].body" "$YAML_FILE")
        milestone=$(yq eval ".issues[$i].milestone" "$YAML_FILE")

        # Processar labels
        local labels_list=()
        local labels_count_issue
        labels_count_issue=$(yq eval ".issues[$i].labels | length" "$YAML_FILE")

        if [[ "$labels_count_issue" != "0" ]]; then
            for ((j=0; j<labels_count_issue; j++)); do
                local label
                label=$(yq eval ".issues[$i].labels[$j]" "$YAML_FILE")
                labels_list+=("$label")
            done
        fi

        # Processar assignees
        local assignees_list=()
        local assignees_count_issue
        assignees_count_issue=$(yq eval ".issues[$i].assignees | length" "$YAML_FILE")

        if [[ "$assignees_count_issue" != "0" ]]; then
            for ((k=0; k<assignees_count_issue; k++)); do
                local assignee
                assignee=$(yq eval ".issues[$i].assignees[$k]" "$YAML_FILE")
                assignees_list+=("$assignee")
            done
        fi

        # Gerar checklist de tasks
        local checklist
        checklist=$(generate_checklist "$i")

        # Verificar se issue já existe
        local existing_issue
        existing_issue=$(get_issue_number_by_title "$title")

        if [[ -n "$existing_issue" ]] && [[ "$existing_issue" != "null" ]]; then
            log "INFO" "Issue '$title' já existe (#$existing_issue)"

            # Verificar e atualizar checklist se necessário
            if need_tasks_update "$existing_issue" "$checklist"; then
                update_issue_checklist "$existing_issue" "$checklist"
            else
                log "INFO" "Checklist da issue #$existing_issue já está atualizado"
            fi

            # Garantir que está no projeto
            add_issue_to_project "$existing_issue"

        else
            # Criar nova issue
            log "INFO" "Criando issue: '$title'"

            # Combinar body com checklist
            local full_body="$body$checklist"

            # Construir comando base
            local gh_cmd=("gh" "issue" "create" "--repo" "$OWNER/$REPO" "--title" "$title")

            # Adicionar body se não for null
            if [[ "$full_body" != "null" ]]; then
                gh_cmd+=("--body" "$full_body")
            fi

            # Adicionar labels se existirem
            if [[ ${#labels_list[@]} -gt 0 ]]; then
                for label in "${labels_list[@]}"; do
                    gh_cmd+=("--label" "$label")
                done
            fi

            # Adicionar milestone se não for null
            if [[ "$milestone" != "null" ]]; then
                gh_cmd+=("--milestone" "$milestone")
            fi

            # Adicionar assignees se existirem
            if [[ ${#assignees_list[@]} -gt 0 ]]; then
                for assignee in "${assignees_list[@]}"; do
                    gh_cmd+=("--assignee" "$assignee")
                done
            fi

            # Executar comando
            if issue_url=$("${gh_cmd[@]}" 2>/dev/null); then
                issue_number=$(echo "$issue_url" | grep -o '[0-9]\+$')
                log "SUCCESS" "Issue '$title' criada com sucesso (#$issue_number)"

                # Adicionar issue ao projeto
                add_issue_to_project "$issue_number"
            else
                log "ERROR" "Falha ao criar issue '$title'"
            fi
        fi
    done
}

# =============================================================================
# FUNÇÃO PRINCIPAL
# =============================================================================

# Função principal
main() {
    log "INFO" "Iniciando GitHub Project Manager..."
    log "INFO" "Data: $(date)"

    # Verificar dependências
    check_dependencies

    # Validar arquivo YAML
    validate_yaml "$YAML_FILE"

    # Ler configurações
    read_config

    # Criar componentes do projeto
    create_labels
    create_milestones
    create_project
    process_issues

    log "SUCCESS" "Script executado com sucesso!"
    log "INFO" "Projeto: https://github.com/$OWNER/$REPO/projects"
    log "INFO" "Issues: https://github.com/$OWNER/$REPO/issues"
}

# =============================================================================
# EXECUÇÃO
# =============================================================================

# Verificar se arquivo YAML foi fornecido como argumento
if [[ $# -gt 0 ]]; then
    YAML_FILE="$1"
fi

# Executar função principal
main "$@"
