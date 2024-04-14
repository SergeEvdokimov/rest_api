from requests import get, post, delete, put

print(get('http://localhost:5000/api/v2/jobs').json())
print(get('http://localhost:5000/api/v2/jobs/1').json())
print(get('http://localhost:5000/api/v2/jobs/18').json())
print(get('http://localhost:5000/api/v2/jobs/q').json())

# print(post('http://localhost:5000/api/jobs', json={'team_leader': 2,
#                                                    'job': 'job',
#                                                    'work_size': 1,
#                                                    'collaborators': '2, 5',
#                                                    'start_date': 1,
#                                                    'end_date': 1,
#                                                    'is_finished': True,
#                                                    'category': 1}).json())
# # start_date, end_date - числа
#
# print(post('http://localhost:5000/api/jobs', json={'team_leader': '2',
#                                                    'job': 'job',
#                                                    'work_size': 1,
#                                                    'collaborators': '2, 5',
#                                                    'start_date': '1',
#                                                    'end_date': '1',
#                                                    'is_finished': True,
#                                                    'category': 1}).json())
# # team_leader - строка
#
# print(post('http://localhost:5000/api/jobs', json={'team_leader': 2,
#                                                    'job': 'job',
#                                                    'work_size': 1,
#                                                    'collaborators': '2, 5',
#                                                    'start_date': '1',
#                                                    'end_date': '1',
#                                                    'is_finished': 'True',
#                                                    'category': 1}).json())
# # is_finished - строка
#
# print(get('http://localhost:5000/api/jobs').json())


# print(delete('http://localhost:5000/api/jobs/999').json())
# # работы с id = 999 нет в базе
#
# print(delete('http://localhost:5000/api/jobs/2').json())
# # удалилось

print(get('http://localhost:5000/api/v2/jobs').json())
print(post('http://localhost:5000/api/v2/jobs', json={'team_leader': 2,
                                                  'job': 'job',
                                                  'work_size': 1,
                                                  'collaborators': '2, 5',
                                                  'start_date': '2024-04-01',
                                                  'end_date': '2024-04-01',
                                                  'is_finished': True,
                                                  'category': 1}).json())
print(post('http://localhost:5000/api/v2/jobs', json={'team_leader': 2,
                                                  'job': 'job',
                                                  'work_size': 1,
                                                  'collaborators': '2, 5',
                                                  'start_date': '2024-04-01',
                                                  'end_date': '2024-04-01',
                                                  'is_finished': 'True',
                                                  'category': 1}).json())
print(post('http://localhost:5000/api/v2/jobs', json={'team_leader': '2',
                                                  'job': 'job',
                                                  'work_size': 1,
                                                  'collaborators': '2, 5',
                                                  'start_date': '2024-04-01',
                                                  'end_date': '2024-04-01',
                                                  'is_finished': True,
                                                  'category': 1}).json())
print(get('http://localhost:5000/api/v2/jobs').json())
