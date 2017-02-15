"""
Code that goes along with the Airflow tutorial located at:
https://github.com/airbnb/airflow/blob/master/airflow/example_dags/tutorial.py

Config:
'{"target_class":"n04105893", "image_tag_path":"/Users/khaxis/workspace/image_tags/"}'
"""
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta


default_args = {
    'owner': 'khaxis',
    'depends_on_past': False,
    'start_date': datetime(2015, 6, 1),
    'email': ['airflow@airflow.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}

dag = DAG('full_chain', default_args=default_args,
                       schedule_interval=None)

# t1, t2 and t3 are examples of tasks created by instantiating operators
make_pool_operator = BashOperator(
    task_id='make_pool',
    bash_command="""
        export WORKING_DIR={{ dag_run.conf["image_tag_path"] if dag_run else "." }};
        export TARGET_CLASS={{ dag_run.conf["target_class"] if dag_run else "" }};
        export DST=$(mktemp);
        cd $WORKING_DIR;
        python -m learning_utils.make_pool --target "$TARGET_CLASS" --out $DST;
        cat $DST

        """,
    xcom_push=True,
    dag=dag)

get_pool_stats_operator = BashOperator(
    task_id='get_pool_stats',
    bash_command="""
        export WORKING_DIR={{ dag_run.conf["image_tag_path"] if dag_run else "." }};
        export POOL={{ ti.xcom_pull("make_pool") }};
        export DST=$(mktemp);
        cd $WORKING_DIR;
        python -m learning_utils.get_pool_stats --pool $POOL --out $DST;
        echo $DST
        """,
    xcom_push=True,
    dag=dag)

get_sampled_or_original_pool_operator = BashOperator(
    task_id='get_sampled_or_original_pool',
    bash_command="""
        export WORKING_DIR={{ dag_run.conf["image_tag_path"] if dag_run else "." }};
        export POOL={{ ti.xcom_pull("make_pool") }};
        export POOL_STATS_PATH={{ ti.xcom_pull("get_pool_stats") }};
        export SAMPLED_POOL_SIZE={{ dag_run.conf["sampled_pool_size"] if dag_run else "." }};
        export DST=$(mktemp);

        export POOL_SIZE=$(python -c "import json; print json.load(open('$POOL_STATS_PATH'))['pool_size']")
        export POOL_DESCRIPTION="$(python -c "import json; print json.load(open('$POOL_STATS_PATH'))['description']")"
        export RATIO=$(python -c "print 1.0 * $SAMPLED_POOL_SIZE / $POOL_SIZE")
        if [ $(echo " $RATIO < 1.0" | bc) -eq 1 ]
        then
            cd $WORKING_DIR;
            python -m learning_utils.sample_pool --pool $POOL --description "POOL_DESCRIPTION - Sampled $SAMPLED_POOL_SIZE instances" --rate $RATIO --out $DST;
            cat $DST
        else
            echo $POOL;
        fi;

        """,
    xcom_push=True,
    dag=dag)

fetch_pool_operator = BashOperator(
    task_id='fetch_pool',
    bash_command="""
        export WORKING_DIR={{ dag_run.conf["image_tag_path"] if dag_run else "." }};
        export POOL={{ ti.xcom_pull("get_sampled_or_original_pool") }};
        export DST=$(mktemp);
        cd $WORKING_DIR;
        python -m learning_utils.fetch_pool --pool $POOL;
        """,
    dag=dag)

train_classifier_operator = BashOperator(
    task_id='train_classifier',
    bash_command="""
        export WORKING_DIR={{ dag_run.conf["image_tag_path"] if dag_run else "." }};
        export POOL={{ ti.xcom_pull("get_sampled_or_original_pool") }};
        export TARGET_CLASS={{ dag_run.conf["target_class"] if dag_run else "" }};
        export DST=$(mktemp);
        cd $WORKING_DIR;
        python -m learning_utils.train_classifier --pool-id $POOL --slices bowSift100 --name "$TARGET_CLASS classifier" --nid $TARGET_CLASS --out $DST;
        cat $DST
        """,
    xcom_push=True,
    dag=dag)


get_pool_stats_operator.set_upstream(make_pool_operator)
get_sampled_or_original_pool_operator.set_upstream([make_pool_operator, get_pool_stats_operator])
fetch_pool_operator.set_upstream(get_sampled_or_original_pool_operator)
train_classifier_operator.set_upstream(fetch_pool_operator)
