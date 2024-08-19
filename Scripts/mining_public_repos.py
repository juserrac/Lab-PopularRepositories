import requests
import csv
from datetime import datetime
import os

token = os.getenv("git - code") ## tirei o meu pq o git considerou a info secreta e não me deixou commitar
headers = {"Authorization": f"Bearer {token}"}

# Função para verificar a resposta da API
def check_response(response):
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch repository details: {response.status_code} - {response.text}")

# Consulta GraphQL para obter dados dos repositórios
def query_repositories(username):
    query = '''
    query($username: String!) {
      user(login: $username) {
        repositories(first: 100) {
          nodes {
            name
            createdAt
            updatedAt
            pullRequests(states: [MERGED], first: 100) {
              totalCount
            }
            releases(first: 100) {
              totalCount
            }
            languages(first: 1) {
              nodes {
                name
              }
            }
            issues(states: [OPEN, CLOSED], first: 100) {
              totalCount
              nodes {
                state
              }
            }
          }
        }
      }
    }
    '''
    variables = {'username': username}
    url = 'https://graphql.github.com/graphql'
    try:
        response = requests.post(url, headers=HEADERS, json={'query': query, 'variables': variables})
        return check_response(response)
    except Exception as e:
        print(f"Erro ao obter dados de repositórios: {e}")
        return {}

# Função para calcular a idade do repositório
def repo_age(created_at):
    created_date = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%SZ')
    age_days = (datetime.utcnow() - created_date).days
    return age_days

# Função para calcular o total de pull requests aceitas
def get_pull_requests_count(pull_requests):
    return pull_requests['totalCount'] if 'totalCount' in pull_requests else 0

# Função para calcular o total de releases
def get_releases_count(releases):
    return releases['totalCount'] if 'totalCount' in releases else 0

# Função para calcular o tempo desde a última atualização
def time_since_last_update(updated_at):
    updated_date = datetime.strptime(updated_at, '%Y-%m-%dT%H:%M:%SZ')
    days_since_update = (datetime.utcnow() - updated_date).days
    return days_since_update

# Função para obter a linguagem primária do repositório
def get_primary_language(languages):
    if 'nodes' in languages and languages['nodes']:
        return languages['nodes'][0]['name']
    return 'N/A'

# Função para calcular o percentual de issues fechadas
def get_issues_closed_ratio(issues):
    total_issues = issues['totalCount'] if 'totalCount' in issues else 0
    closed_issues = sum(1 for issue in issues.get('nodes', []) if issue['state'] == 'CLOSED')
    return closed_issues / total_issues if total_issues > 0 else 0

# Função principal para minerar dados dos repositórios
def mine_popular_repos(username):
    data = []
    result = query_repositories(username)
    repositories = result.get('data', {}).get('user', {}).get('repositories', {}).get('nodes', [])
    
    for repo in repositories:
        repo_data = {
            'Name': repo['name'],
            'Age (days)': repo_age(repo['createdAt']),
            'Pull Requests Accepted': get_pull_requests_count(repo['pullRequests']),
            'Total Releases': get_releases_count(repo['releases']),
            'Days Since Last Update': time_since_last_update(repo['updatedAt']),
            'Primary Language': get_primary_language(repo['languages']),
            'Issues Closed Ratio': get_issues_closed_ratio(repo['issues'])
        }
        data.append(repo_data)

    # Salvando os dados em um arquivo CSV usando a biblioteca padrão
    with open('popular_repos_data.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

    print("Dados minerados e salvos em 'popular_repos_data.csv'.")

if __name__ == "__main__":
    USERNAME = 'juserrac'  
    mine_popular_repos(USERNAME)