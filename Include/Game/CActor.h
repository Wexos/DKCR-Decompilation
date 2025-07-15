#pragma once

#include "Game/CEntity.h"

class CDamageInfo;
class CDamageResult;
class CStateManager;
class CVector3f;
class TUniqueId;

class CActor : public CEntity
{
public:
    enum EDamageOriginator
    {

    };

    ~CActor() override;

    bool TypesMatch(int) const override;
    void PreThink(f32, CStateManager&) override;
    void Think(f32, CStateManager&) override;
    void AcceptScriptMsg(CStateManager&, const CScriptMsg&) override;
    void SetActive(CStateManager&, bool) override;
    void Unk24() override;
    virtual void SetTransformDirty();
    virtual void Unk2C();
    virtual void* HealthInfo();
    virtual void Unk34();
    virtual void GetDamageVulnerability() const;
    virtual void Unk3C();
    virtual void Unk40();
    virtual void NotifyDamageEvent(CStateManager&, TUniqueId, const CDamageInfo&, const CDamageResult&, EDamageOriginator);
    virtual void ProcessAndNotifyDamage(CStateManager&, TUniqueId, const CDamageInfo&);
    virtual void GetTouchBounds() const;
    virtual void GetDamageBounds() const;
    virtual void GetDetailedTouchBounds() const;
    virtual void DetailedTouchBounds();
    virtual void Touch(CStateManager&, CActor&);
    virtual bool IsOnScreen(const CStateManager&) const;
    virtual bool IsCompletelyOnScreen(const CStateManager&) const;
    virtual void GetAimPosition(const CStateManager&,f32) const;
    virtual void GetLookAtPosition(const CStateManager&) const;
    virtual f32 GetPlatformRiderDecayTime() const;
    virtual void NotifyMaterialListChanged();
};
