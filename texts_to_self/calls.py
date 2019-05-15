from texts_to_self import tasks

tasks.sleep.delay('Flask is Live!', seconds=5)

tasks.sleep.delay(run_jobs(), seconds=60)

