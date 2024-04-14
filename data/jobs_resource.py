from flask import jsonify
from data import db_session
from data.jobs import Jobs
from flask_restful import reqparse, abort, Resource


def abort_if_job_not_found(job_id):
    session = db_session.create_session()
    jobs = session.get(Jobs, job_id)
    if not jobs:
        abort(404, message=f"Job {job_id} not found")


class JobsResource(Resource):
    def get(self, job_id):
        abort_if_job_not_found(job_id)
        session = db_session.create_session()
        jobs = session.get(Jobs, job_id)
        return jsonify({'jobs': jobs.to_dict(
            only=('team_leader', 'job', 'work_size', 'collaborators', 'start_date',
                  'end_date', 'is_finished', 'category'))})

    def delete(self, job_id):
        abort_if_job_not_found(job_id)
        session = db_session.create_session()
        jobs = session.get(Jobs, job_id)
        session.delete(jobs)
        session.commit()
        return jsonify({'success': 'OK'})


parser = reqparse.RequestParser()
parser.add_argument('team_leader', required=True)
parser.add_argument('job', required=True)
parser.add_argument('work_size', required=True, type=int)
parser.add_argument('collaborators', required=True)
parser.add_argument('start_date', required=True)
parser.add_argument('end_date', required=True)
parser.add_argument('is_finished', required=True, type=bool)
parser.add_argument('category', required=True, type=int)


class JobsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        jobs = session.query(Jobs).all()
        return jsonify({'jobs': [item.to_dict(
            only=('team_leader', 'job', 'work_size', 'collaborators', 'start_date',
                  'end_date', 'is_finished', 'category')) for item in jobs]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        jobs = Jobs(
            team_leader=args['team_leader'],
            job=args['job'],
            work_size=args['work_size'],
            collaborators=args['collaborators'],
            start_date=args['start_date'],
            end_date=args['end_date'],
            is_finished=args['is_finished'],
            category=args['category']
        )
        session.add(jobs)
        session.commit()
        return jsonify({'id': jobs.id})
    