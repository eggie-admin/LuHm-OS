import sqlite3, unittest
from tools.typedSqlStub import openStub,addEvent,putNumeric,putText,putBoolean,putManifest,orderedEvents
S='a'*40
class TypedStubTests(unittest.TestCase):
    def setUp(self):
        self.db=openStub(); addEvent(self.db,'firstEvent','testTask',S,'testScope','lum',1,1,'2026-10-12T15:00:00Z')
    def tearDown(self): self.db.close()
    def test_int(self):
        putNumeric(self.db,'firstEvent','requests','integer',42)
        self.assertEqual(self.db.execute('SELECT integerValue FROM numericStream').fetchone()[0],42)
    def test_bool_not_int(self):
        with self.assertRaises(ValueError): putNumeric(self.db,'firstEvent','requests','integer',True)
    def test_float_finite(self):
        putNumeric(self.db,'firstEvent','durationMs','float',0.25)
        for v in (float('nan'),float('inf')):
            with self.assertRaises(ValueError): putNumeric(self.db,'firstEvent','bad','float',v)
    def test_fixed_precision(self):
        putNumeric(self.db,'firstEvent','rate','fixed','0.123456',6)
        self.assertEqual(self.db.execute('SELECT scaledValue FROM numericStream').fetchone()[0],123456)
        with self.assertRaises(ValueError): putNumeric(self.db,'firstEvent','otherRate','fixed','0.1234567',6)
    def test_text(self):
        putText(self.db,'firstEvent','sourceText','音楽')
        self.assertEqual(self.db.execute('SELECT textValue FROM textStream').fetchone()[0],'音楽')
    def test_booleans(self):
        putBoolean(self.db,'firstEvent','green',None)
        with self.assertRaises(ValueError): putBoolean(self.db,'firstEvent','bad',1)
    def test_sql_strict(self):
        with self.assertRaises(sqlite3.IntegrityError): self.db.execute("INSERT INTO booleanStream VALUES('firstEvent','bad',3)")
    def test_foreign_key(self):
        with self.assertRaises(sqlite3.IntegrityError): putText(self.db,'missingEvent','field','x')
    def test_manifest(self):
        m={'schema':'luhmOs.aiTaskManifest.v2','taskId':'testTask','sourceRef':S,'scopeId':'testScope','providerId':'openAi','capabilityId':'research','authority':{'mutation':False,'green':False,'crown':False}}
        putManifest(self.db,'firstEvent',m)
        m['authority']['crown']=True
        with self.assertRaises(ValueError): putManifest(self.db,'firstEvent',m)
    def test_eighth_note(self):
        with self.assertRaises(ValueError): addEvent(self.db,'newEvent','testTask',S,'testScope','lum',2,9,'2026-10-12T15:00:00Z')
    def test_sort(self):
        addEvent(self.db,'secondEvent','testTask',S,'testScope','lum',2,8,'2026-10-12T15:00:00Z')
        self.assertEqual([r['sequenceId'] for r in orderedEvents(self.db,'testTask',S,'testScope')],[1,2])
    def test_rollback(self):
        with self.assertRaises(ValueError):
            with self.db:
                putText(self.db,'firstEvent','label','transient')
                putNumeric(self.db,'firstEvent','rate','fixed','0.0000001',6)
        self.assertEqual(self.db.execute('SELECT count(*) FROM textStream').fetchone()[0],0)

    def test_sql_rejects_non_hex_source_ref(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                'INSERT INTO streamEvent(eventId,taskId,sourceRef,scopeId,workerId,sequenceId,eighthNote,observedAt) VALUES (?,?,?,?,?,?,?,?)',
                ('badEvent','testTask','g'*40,'testScope','lum',2,1,'2026-10-12T15:00:00Z')
            )

    def test_sql_rejects_non_utc_observed_time(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                'INSERT INTO streamEvent(eventId,taskId,sourceRef,scopeId,workerId,sequenceId,eighthNote,observedAt) VALUES (?,?,?,?,?,?,?,?)',
                ('badEvent','testTask',S,'testScope','lum',2,1,'2026-10-12T15:00:00')
            )

    def test_sql_rejects_bad_artifact_hash(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                'INSERT INTO artifactPointer(artifactId,eventId,fileName,sha256,storageLane,logicalFileRef,sizeBytes) VALUES (?,?,?,?,?,?,?)',
                ('artifactOne','firstEvent','sample.glb','z'*64,'googleDriveDurable','privateAssetRef',12)
            )

    def test_parameterized_text_is_not_sql(self):
        original = "x'); DROP TABLE streamEvent; --"
        putText(self.db,'firstEvent','untrustedLabel',original)
        self.assertEqual(self.db.execute(
            "SELECT textValue FROM textStream WHERE fieldName=?", ('untrustedLabel',)).fetchone()[0],original)
        self.assertEqual(self.db.execute("SELECT count(*) FROM streamEvent").fetchone()[0],1)

if __name__=='__main__': unittest.main()
